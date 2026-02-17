"""Tests for standardized response utilities."""

from okta_mcp_server.utils.response import (
    PaginatedResponse,
    ToolResponse,
    error_response,
    success_response,
)


class TestToolResponse:
    """Tests for ToolResponse dataclass."""

    def test_success_to_dict_with_data(self):
        resp = ToolResponse(success=True, data={"id": "123"})
        result = resp.to_dict()
        assert result == {"success": True, "data": {"id": "123"}}

    def test_success_to_dict_without_data(self):
        resp = ToolResponse(success=True)
        result = resp.to_dict()
        assert result == {"success": True}

    def test_failure_to_dict_with_error(self):
        resp = ToolResponse(success=False, error="Something went wrong")
        result = resp.to_dict()
        assert result == {"success": False, "error": "Something went wrong"}

    def test_failure_to_dict_with_error_and_data(self):
        resp = ToolResponse(success=False, data={"partial": True}, error="Partial failure")
        result = resp.to_dict()
        assert result == {"success": False, "data": {"partial": True}, "error": "Partial failure"}

    def test_none_data_excluded_from_dict(self):
        resp = ToolResponse(success=True, data=None)
        assert "data" not in resp.to_dict()

    def test_none_error_excluded_from_dict(self):
        resp = ToolResponse(success=True, error=None)
        assert "error" not in resp.to_dict()


class TestPaginatedResponse:
    """Tests for PaginatedResponse dataclass."""

    def test_to_dict_with_items(self):
        resp = PaginatedResponse(success=True, data=[{"id": "1"}, {"id": "2"}], total_fetched=2)
        result = resp.to_dict()
        assert result["items"] == [{"id": "1"}, {"id": "2"}]
        assert result["total_fetched"] == 2
        assert result["success"] is True
        assert result["has_more"] is False
        assert result["next_cursor"] is None
        assert result["fetch_all_used"] is False

    def test_to_dict_with_none_data_returns_empty_list(self):
        resp = PaginatedResponse(success=True, data=None)
        assert resp.to_dict()["items"] == []

    def test_to_dict_with_pagination_metadata(self):
        resp = PaginatedResponse(
            success=True,
            data=[],
            has_more=True,
            next_cursor="abc123",
            fetch_all_used=False,
            pagination_info={"pages_fetched": 3},
        )
        result = resp.to_dict()
        assert result["has_more"] is True
        assert result["next_cursor"] == "abc123"
        assert result["pagination_info"] == {"pages_fetched": 3}

    def test_to_dict_excludes_pagination_info_when_none(self):
        resp = PaginatedResponse(success=True, data=[], pagination_info=None)
        assert "pagination_info" not in resp.to_dict()

    def test_to_dict_includes_error(self):
        resp = PaginatedResponse(success=False, data=[], error="API failure")
        result = resp.to_dict()
        assert result["error"] == "API failure"
        assert result["success"] is False

    def test_to_dict_excludes_error_when_none(self):
        resp = PaginatedResponse(success=True, data=[])
        assert "error" not in resp.to_dict()


class TestSuccessResponse:
    """Tests for success_response helper."""

    def test_with_data(self):
        result = success_response(data={"user": "test"})
        assert result == {"success": True, "data": {"user": "test"}}

    def test_without_data(self):
        result = success_response()
        assert result == {"success": True}

    def test_with_list_data(self):
        result = success_response(data=[1, 2, 3])
        assert result == {"success": True, "data": [1, 2, 3]}

    def test_with_string_data(self):
        result = success_response(data="ok")
        assert result == {"success": True, "data": "ok"}


class TestErrorResponse:
    """Tests for error_response helper."""

    def test_error_only(self):
        result = error_response("bad request")
        assert result == {"success": False, "error": "bad request"}

    def test_error_with_partial_data(self):
        result = error_response("partial failure", data={"partial": True})
        assert result == {"success": False, "data": {"partial": True}, "error": "partial failure"}
