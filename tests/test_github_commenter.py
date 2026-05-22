import pytest
from unittest.mock import patch, MagicMock
from src.github_commenter import (
    find_existing_comment,
    post_comment,
    update_comment,
    upsert_comment,
    COMMENT_MARKER,
)

REPO = "owner/repo"
PR_NUMBER = 42
TOKEN = "fake-token"
BODY = "## Dependency Graph\n```mermaid\ngraph LR\n```"


def make_mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    return mock


class TestFindExistingComment:
    def test_returns_comment_id_when_marker_found(self):
        comments = [{"id": 101, "body": f"{COMMENT_MARKER}\nsome content"}]
        with patch("src.github_commenter.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(comments)
            result = find_existing_comment(REPO, PR_NUMBER, TOKEN)
        assert result == 101

    def test_returns_none_when_no_marker(self):
        comments = [{"id": 202, "body": "unrelated comment"}]
        with patch("src.github_commenter.requests.get") as mock_get:
            mock_get.return_value = make_mock_response(comments)
            result = find_existing_comment(REPO, PR_NUMBER, TOKEN)
        assert result is None

    def test_returns_none_for_empty_comments(self):
        with patch("src.github_commenter.requests.get") as mock_get:
            mock_get.return_value = make_mock_response([])
            result = find_existing_comment(REPO, PR_NUMBER, TOKEN)
        assert result is None


class TestPostComment:
    def test_posts_comment_with_marker(self):
        with patch("src.github_commenter.requests.post") as mock_post:
            mock_post.return_value = make_mock_response({"id": 303})
            result = post_comment(REPO, PR_NUMBER, BODY, TOKEN)
        assert result == {"id": 303}
        _, kwargs = mock_post.call_args
        assert COMMENT_MARKER in kwargs["json"]["body"]
        assert BODY in kwargs["json"]["body"]


class TestUpdateComment:
    def test_updates_comment_with_marker(self):
        with patch("src.github_commenter.requests.patch") as mock_patch:
            mock_patch.return_value = make_mock_response({"id": 404})
            result = update_comment(REPO, 404, BODY, TOKEN)
        assert result == {"id": 404}
        _, kwargs = mock_patch.call_args
        assert COMMENT_MARKER in kwargs["json"]["body"]


class TestUpsertComment:
    def test_posts_new_comment_when_none_exists(self):
        with patch("src.github_commenter.find_existing_comment", return_value=None), \
             patch("src.github_commenter.post_comment", return_value={"id": 1}) as mock_post:
            result = upsert_comment(REPO, PR_NUMBER, BODY, TOKEN)
        mock_post.assert_called_once_with(REPO, PR_NUMBER, BODY, TOKEN)
        assert result == {"id": 1}

    def test_updates_existing_comment_when_found(self):
        with patch("src.github_commenter.find_existing_comment", return_value=99), \
             patch("src.github_commenter.update_comment", return_value={"id": 99}) as mock_update:
            result = upsert_comment(REPO, PR_NUMBER, BODY, TOKEN)
        mock_update.assert_called_once_with(REPO, 99, BODY, TOKEN)
        assert result == {"id": 99}
