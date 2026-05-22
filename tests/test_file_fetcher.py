import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import urllib.error

from src.file_fetcher import (
    fetch_file_at_ref,
    detect_dependency_file,
    fetch_base_and_head,
    SUPPORTED_FILES,
)


def make_mock_response(content_str: str):
    encoded = base64.b64encode(content_str.encode()).decode()
    payload = json.dumps({"encoding": "base64", "content": encoded}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = payload
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestFetchFileAtRef(unittest.TestCase):
    @patch("src.file_fetcher.urllib.request.urlopen")
    def test_returns_decoded_content(self, mock_urlopen):
        mock_urlopen.return_value = make_mock_response("flask==2.0.0\n")
        result = fetch_file_at_ref("owner/repo", "requirements.txt", "main", "tok")
        self.assertEqual(result, "flask==2.0.0\n")

    @patch("src.file_fetcher.urllib.request.urlopen")
    def test_returns_none_on_404(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=404, msg="Not Found", hdrs={}, fp=None
        )
        result = fetch_file_at_ref("owner/repo", "requirements.txt", "main", "tok")
        self.assertIsNone(result)

    @patch("src.file_fetcher.urllib.request.urlopen")
    def test_raises_on_non_404_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=500, msg="Server Error", hdrs={}, fp=None
        )
        with self.assertRaises(urllib.error.HTTPError):
            fetch_file_at_ref("owner/repo", "requirements.txt", "main", "tok")


class TestDetectDependencyFile(unittest.TestCase):
    @patch("src.file_fetcher.fetch_file_at_ref")
    def test_detects_requirements_txt(self, mock_fetch):
        mock_fetch.side_effect = lambda repo, path, ref, token: (
            "flask==2.0.0\n" if path == "requirements.txt" else None
        )
        filename, content = detect_dependency_file("owner/repo", "main", "tok")
        self.assertEqual(filename, "requirements.txt")
        self.assertIn("flask", content)

    @patch("src.file_fetcher.fetch_file_at_ref")
    def test_returns_none_when_no_file_found(self, mock_fetch):
        mock_fetch.return_value = None
        filename, content = detect_dependency_file("owner/repo", "main", "tok")
        self.assertIsNone(filename)
        self.assertIsNone(content)

    @patch("src.file_fetcher.fetch_file_at_ref")
    def test_prefers_requirements_txt_over_package_json(self, mock_fetch):
        mock_fetch.return_value = "some content"
        filename, _ = detect_dependency_file("owner/repo", "main", "tok")
        self.assertEqual(filename, SUPPORTED_FILES[0])


class TestFetchBaseAndHead(unittest.TestCase):
    @patch("src.file_fetcher.fetch_file_at_ref")
    @patch("src.file_fetcher.detect_dependency_file")
    def test_returns_both_contents(self, mock_detect, mock_fetch):
        mock_detect.return_value = ("requirements.txt", "flask==2.1.0\n")
        mock_fetch.return_value = "flask==2.0.0\n"
        result = fetch_base_and_head("owner/repo", "main", "feature", "tok")
        self.assertEqual(result["filename"], "requirements.txt")
        self.assertEqual(result["head_content"], "flask==2.1.0\n")
        self.assertEqual(result["base_content"], "flask==2.0.0\n")

    @patch("src.file_fetcher.detect_dependency_file")
    def test_returns_empty_when_no_file_detected(self, mock_detect):
        mock_detect.return_value = (None, None)
        result = fetch_base_and_head("owner/repo", "main", "feature", "tok")
        self.assertIsNone(result["filename"])
        self.assertEqual(result["base_content"], "")
        self.assertEqual(result["head_content"], "")
