# Utility Module Test Coverage Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fill the test coverage gap for all utility modules (response, validators, retry, pagination, client, server) — currently at 11% utility coverage vs 100% tool coverage.

**Architecture:** Each utility module gets a dedicated test file following the existing pattern: pytest-asyncio, `tests/` directory, mock fixtures from `conftest.py`. Tests verify actual behavior, not mock behavior.

**Tech Stack:** Python 3.x, pytest, pytest-asyncio, unittest.mock, tenacity

---

### Task 1: Test Response Utilities

**Files:**
- Create: `tests/test_response.py`
- Source: `src/okta_mcp_server/utils/response.py`

**Step 1: Write the tests**

```python
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
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_response.py -v`
Expected: All 17 tests PASS

**Step 3: Commit**

```bash
git add tests/test_response.py
git commit -m "test: add comprehensive tests for response utilities"
```

---

### Task 2: Test Validators Utilities

**Files:**
- Create: `tests/test_validators.py`
- Source: `src/okta_mcp_server/utils/validators.py`

**Step 1: Write the tests**

```python
"""Tests for input validation utilities."""

import pytest

from okta_mcp_server.utils.validators import (
    ValidationError,
    validate_email,
    validate_iso_timestamp,
    validate_limit,
    validate_okta_id,
    validate_profile_dict,
    validate_required_string,
)


class TestValidateEmail:
    """Tests for validate_email."""

    def test_valid_email(self):
        valid, err = validate_email("user@example.com")
        assert valid is True
        assert err is None

    def test_valid_email_with_plus(self):
        valid, err = validate_email("user+tag@example.com")
        assert valid is True

    def test_empty_string(self):
        valid, err = validate_email("")
        assert valid is False
        assert "required" in err

    def test_missing_at_sign(self):
        valid, err = validate_email("userexample.com")
        assert valid is False
        assert "Invalid email format" in err

    def test_missing_domain(self):
        valid, err = validate_email("user@")
        assert valid is False

    def test_too_long(self):
        valid, err = validate_email("a" * 250 + "@b.com")
        assert valid is False
        assert "too long" in err

    def test_non_string_type(self):
        valid, err = validate_email(12345)
        assert valid is False
        assert "string" in err


class TestValidateOktaId:
    """Tests for validate_okta_id."""

    def test_valid_id(self):
        valid, err = validate_okta_id("00u1abc123def456")
        assert valid is True
        assert err is None

    def test_valid_id_with_hyphens_underscores(self):
        valid, err = validate_okta_id("abc-def_123")
        assert valid is True

    def test_empty_string(self):
        valid, err = validate_okta_id("")
        assert valid is False
        assert "required" in err

    def test_too_long(self):
        valid, err = validate_okta_id("a" * 101)
        assert valid is False
        assert "too long" in err

    def test_invalid_characters(self):
        valid, err = validate_okta_id("abc@def")
        assert valid is False
        assert "invalid characters" in err

    def test_custom_field_name(self):
        valid, err = validate_okta_id("", field_name="user_id")
        assert "user_id" in err

    def test_non_string_type(self):
        valid, err = validate_okta_id(12345)
        assert valid is False
        assert "string" in err


class TestValidateIsoTimestamp:
    """Tests for validate_iso_timestamp."""

    def test_valid_utc_timestamp(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00Z")
        assert valid is True
        assert err is None

    def test_valid_with_milliseconds(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00.123Z")
        assert valid is True

    def test_valid_with_timezone_offset(self):
        valid, err = validate_iso_timestamp("2024-01-15T10:30:00+05:30")
        assert valid is True

    def test_empty_string_is_optional(self):
        valid, err = validate_iso_timestamp("")
        assert valid is True
        assert err is None

    def test_invalid_format(self):
        valid, err = validate_iso_timestamp("not-a-timestamp")
        assert valid is False
        assert "ISO 8601" in err

    def test_non_string_type(self):
        valid, err = validate_iso_timestamp(12345)
        assert valid is False
        assert "string" in err


class TestValidateLimit:
    """Tests for validate_limit."""

    def test_none_returns_default(self):
        value, warn = validate_limit(None)
        assert value == 20
        assert warn is None

    def test_valid_value(self):
        value, warn = validate_limit(50)
        assert value == 50
        assert warn is None

    def test_below_minimum(self):
        value, warn = validate_limit(5)
        assert value == 20
        assert "below minimum" in warn

    def test_above_maximum(self):
        value, warn = validate_limit(200)
        assert value == 100
        assert "exceeds maximum" in warn

    def test_custom_bounds(self):
        value, warn = validate_limit(5, min_val=1, max_val=10)
        assert value == 5
        assert warn is None

    def test_non_integer_convertible(self):
        value, warn = validate_limit("50")
        assert value == 50

    def test_non_integer_not_convertible(self):
        value, warn = validate_limit("abc")
        assert value == 20
        assert "integer" in warn

    def test_boundary_min(self):
        value, warn = validate_limit(20)
        assert value == 20
        assert warn is None

    def test_boundary_max(self):
        value, warn = validate_limit(100)
        assert value == 100
        assert warn is None


class TestValidateRequiredString:
    """Tests for validate_required_string."""

    def test_valid_string(self):
        valid, err = validate_required_string("hello", "name")
        assert valid is True
        assert err is None

    def test_none_value(self):
        valid, err = validate_required_string(None, "name")
        assert valid is False
        assert "required" in err

    def test_empty_string(self):
        valid, err = validate_required_string("", "name")
        assert valid is False
        assert "empty" in err

    def test_whitespace_only(self):
        valid, err = validate_required_string("   ", "name")
        assert valid is False
        assert "empty" in err

    def test_non_string_type(self):
        valid, err = validate_required_string(123, "name")
        assert valid is False
        assert "string" in err

    def test_field_name_in_error(self):
        valid, err = validate_required_string(None, "email_address")
        assert "email_address" in err


class TestValidateProfileDict:
    """Tests for validate_profile_dict."""

    def test_valid_dict(self):
        valid, err = validate_profile_dict({"firstName": "Test"})
        assert valid is True
        assert err is None

    def test_none_value(self):
        valid, err = validate_profile_dict(None)
        assert valid is False
        assert "required" in err

    def test_non_dict_type(self):
        valid, err = validate_profile_dict("not a dict")
        assert valid is False
        assert "dictionary" in err

    def test_missing_required_fields(self):
        valid, err = validate_profile_dict({"firstName": "Test"}, required_fields=["firstName", "lastName"])
        assert valid is False
        assert "lastName" in err

    def test_all_required_fields_present(self):
        valid, err = validate_profile_dict(
            {"firstName": "Test", "lastName": "User"},
            required_fields=["firstName", "lastName"],
        )
        assert valid is True

    def test_required_field_with_empty_value(self):
        valid, err = validate_profile_dict({"firstName": ""}, required_fields=["firstName"])
        assert valid is False
        assert "firstName" in err

    def test_no_required_fields(self):
        valid, err = validate_profile_dict({})
        assert valid is True


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_attributes(self):
        err = ValidationError("email", "Invalid format")
        assert err.field == "email"
        assert err.message == "Invalid format"

    def test_string_representation(self):
        err = ValidationError("email", "Invalid format")
        assert "email" in str(err)
        assert "Invalid format" in str(err)

    def test_is_exception(self):
        with pytest.raises(ValidationError):
            raise ValidationError("field", "error")
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_validators.py -v`
Expected: All 37 tests PASS

**Step 3: Commit**

```bash
git add tests/test_validators.py
git commit -m "test: add comprehensive tests for input validation utilities"
```

---

### Task 3: Test Retry Utilities

**Files:**
- Create: `tests/test_retry.py`
- Source: `src/okta_mcp_server/utils/retry.py`

**Step 1: Write the tests**

```python
"""Tests for retry utilities."""

import pytest

from okta_mcp_server.utils.retry import RetryableError, retry_on_rate_limit, with_retry


class TestWithRetry:
    """Tests for with_retry decorator."""

    @pytest.mark.asyncio
    async def test_async_function_succeeds_first_try(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await succeed()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retries_on_connection_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("connection refused")
            return "ok"

        result = await fail_then_succeed()
        assert result == "ok"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retries_on_timeout_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def timeout_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("timed out")
            return "ok"

        result = await timeout_then_succeed()
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retries_on_os_error(self):
        call_count = 0

        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        async def os_error_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("network unreachable")
            return "ok"

        result = await os_error_then_succeed()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_async_raises_after_max_attempts(self):
        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        async def always_fail():
            raise ConnectionError("connection refused")

        with pytest.raises(ConnectionError, match="connection refused"):
            await always_fail()

    @pytest.mark.asyncio
    async def test_async_non_retryable_raises_immediately(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def raise_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("bad value")

        with pytest.raises(ValueError):
            await raise_value_error()
        assert call_count == 1

    def test_sync_function_succeeds(self):
        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def succeed():
            return "ok"

        assert succeed() == "ok"

    def test_sync_retries_on_connection_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("refused")
            return "ok"

        result = fail_then_succeed()
        assert result == "ok"
        assert call_count == 3

    def test_sync_raises_after_max_attempts(self):
        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        def always_fail():
            raise ConnectionError("refused")

        with pytest.raises(ConnectionError):
            always_fail()

    def test_sync_non_retryable_raises_immediately(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("bad type")

        with pytest.raises(TypeError):
            raise_type_error()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0, retryable_exceptions=(ValueError,))
        async def custom_retry():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("retryable")
            return "ok"

        result = await custom_retry()
        assert result == "ok"
        assert call_count == 2


class TestRetryOnRateLimit:
    """Tests for retry_on_rate_limit decorator."""

    @pytest.mark.asyncio
    async def test_decorates_async_function(self):
        @retry_on_rate_limit
        async def api_call():
            return "result"

        result = await api_call()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self):
        call_count = 0

        @retry_on_rate_limit
        async def flaky_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("rate limited")
            return "ok"

        result = await flaky_call()
        assert result == "ok"
        assert call_count == 2


class TestRetryableError:
    """Tests for RetryableError exception."""

    def test_message(self):
        err = RetryableError("something failed")
        assert str(err) == "something failed"

    def test_original_error(self):
        original = ConnectionError("conn refused")
        err = RetryableError("wrapper", original_error=original)
        assert err.original_error is original

    def test_default_original_error_is_none(self):
        err = RetryableError("test")
        assert err.original_error is None

    def test_is_exception(self):
        with pytest.raises(RetryableError):
            raise RetryableError("test")
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_retry.py -v`
Expected: All 17 tests PASS

**Step 3: Commit**

```bash
git add tests/test_retry.py
git commit -m "test: add comprehensive tests for retry utilities"
```

---

### Task 4: Test Pagination Utilities

**Files:**
- Create: `tests/test_pagination_utils.py`
- Source: `src/okta_mcp_server/utils/pagination.py`
- Reference: `tests/conftest.py` (MockOktaResponse)

**Step 1: Write the tests**

```python
"""Tests for pagination utility functions."""

import pytest

from okta_mcp_server.utils.pagination import (
    build_query_params,
    create_paginated_response,
    extract_after_cursor,
    paginate_all_results,
)
from tests.conftest import MockOktaResponse


class TestExtractAfterCursor:
    """Tests for extract_after_cursor."""

    def test_extracts_cursor_from_next_url(self):
        response = MockOktaResponse(has_next=True, next_url="/api/v1/users?after=00u1abc123")
        cursor = extract_after_cursor(response)
        assert cursor == "00u1abc123"

    def test_returns_none_when_no_next(self):
        response = MockOktaResponse(has_next=False)
        cursor = extract_after_cursor(response)
        assert cursor is None

    def test_returns_none_for_none_response(self):
        cursor = extract_after_cursor(None)
        assert cursor is None

    def test_handles_url_with_multiple_params(self):
        response = MockOktaResponse(
            has_next=True,
            next_url="/api/v1/users?limit=20&after=cursor123&search=test",
        )
        cursor = extract_after_cursor(response)
        assert cursor == "cursor123"

    def test_returns_none_when_no_after_param(self):
        response = MockOktaResponse(has_next=True, next_url="/api/v1/users?limit=20")
        cursor = extract_after_cursor(response)
        assert cursor is None

    def test_returns_none_when_next_url_is_none(self):
        response = MockOktaResponse(has_next=True, next_url=None)
        # has_next() is True but _next is None
        cursor = extract_after_cursor(response)
        assert cursor is None


class TestPaginateAllResults:
    """Tests for paginate_all_results."""

    @pytest.mark.asyncio
    async def test_single_page(self):
        items = [{"id": "1"}, {"id": "2"}]
        response = MockOktaResponse(has_next=False)
        all_items, info = await paginate_all_results(response, items)
        assert len(all_items) == 2
        assert info["pages_fetched"] == 1
        assert info["stopped_early"] is False

    @pytest.mark.asyncio
    async def test_multiple_pages(self):
        page2_response = MockOktaResponse(has_next=False)
        page1_response = MockOktaResponse(
            has_next=True,
            next_page_data=([{"id": "3"}], page2_response),
        )
        initial_items = [{"id": "1"}, {"id": "2"}]

        all_items, info = await paginate_all_results(page1_response, initial_items, delay_between_requests=0)
        assert len(all_items) == 3
        assert info["pages_fetched"] == 2
        assert info["total_items"] == 3

    @pytest.mark.asyncio
    async def test_respects_max_pages(self):
        # Create a chain that would go 5 pages but limit to 2
        page3_resp = MockOktaResponse(has_next=True, next_page_data=([{"id": "4"}], MockOktaResponse(has_next=True)))
        page2_resp = MockOktaResponse(has_next=True, next_page_data=([{"id": "3"}], page3_resp))
        page1_resp = MockOktaResponse(has_next=True, next_page_data=([{"id": "2"}], page2_resp))

        all_items, info = await paginate_all_results(
            page1_resp, [{"id": "1"}], max_pages=2, delay_between_requests=0
        )
        assert info["pages_fetched"] == 2
        assert info["stopped_early"] is True
        assert "maximum page limit" in info["stop_reason"]

    @pytest.mark.asyncio
    async def test_none_response(self):
        all_items, info = await paginate_all_results(None, [{"id": "1"}])
        assert len(all_items) == 1
        assert info["pages_fetched"] == 1

    @pytest.mark.asyncio
    async def test_none_initial_items(self):
        response = MockOktaResponse(has_next=False)
        all_items, info = await paginate_all_results(response, None)
        assert all_items == []

    @pytest.mark.asyncio
    async def test_error_in_next_page(self):
        """When response.next() returns an error, pagination stops early."""
        class ErrorResponse:
            def has_next(self):
                return True

            async def next(self):
                return None, "API Error: rate limited"

        response = ErrorResponse()
        all_items, info = await paginate_all_results(response, [{"id": "1"}], delay_between_requests=0)
        assert len(all_items) == 1
        assert info["stopped_early"] is True
        assert "API error" in info["stop_reason"]


class TestCreatePaginatedResponse:
    """Tests for create_paginated_response."""

    def test_basic_response(self):
        items = [{"id": "1"}, {"id": "2"}]
        response = MockOktaResponse(has_next=False)
        result = create_paginated_response(items, response)
        assert result["items"] == items
        assert result["total_fetched"] == 2
        assert result["has_more"] is False
        assert result["next_cursor"] is None
        assert result["fetch_all_used"] is False

    def test_with_more_pages(self):
        items = [{"id": "1"}]
        response = MockOktaResponse(has_next=True, next_url="/api/v1/users?after=cursor1")
        result = create_paginated_response(items, response)
        assert result["has_more"] is True
        assert result["next_cursor"] == "cursor1"

    def test_fetch_all_used(self):
        items = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        response = MockOktaResponse(has_next=False)
        result = create_paginated_response(items, response, fetch_all_used=True)
        assert result["fetch_all_used"] is True
        # When fetch_all is used, has_more/next_cursor should not reflect response state
        assert result["has_more"] is False
        assert result["next_cursor"] is None

    def test_with_pagination_info(self):
        items = []
        response = MockOktaResponse(has_next=False)
        info = {"pages_fetched": 5, "total_items": 100}
        result = create_paginated_response(items, response, pagination_info=info)
        assert result["pagination_info"] == info

    def test_without_pagination_info(self):
        items = []
        response = MockOktaResponse(has_next=False)
        result = create_paginated_response(items, response)
        assert "pagination_info" not in result

    def test_none_response(self):
        items = [{"id": "1"}]
        result = create_paginated_response(items, None)
        assert result["has_more"] is False
        assert result["next_cursor"] is None


class TestBuildQueryParams:
    """Tests for build_query_params."""

    def test_empty_params(self):
        params = build_query_params()
        assert params == {}

    def test_search_only(self):
        params = build_query_params(search='profile.email eq "user@example.com"')
        assert params == {"search": 'profile.email eq "user@example.com"'}

    def test_filter_param(self):
        params = build_query_params(filter='status eq "ACTIVE"')
        assert params == {"filter": 'status eq "ACTIVE"'}

    def test_query_param(self):
        params = build_query_params(q="test user")
        assert params == {"q": "test user"}

    def test_pagination_params(self):
        params = build_query_params(after="cursor123", limit=50)
        assert params == {"after": "cursor123", "limit": "50"}

    def test_time_range_params(self):
        params = build_query_params(since="2024-01-01T00:00:00Z", until="2024-01-31T23:59:59Z")
        assert params == {"since": "2024-01-01T00:00:00Z", "until": "2024-01-31T23:59:59Z"}

    def test_kwargs_included(self):
        params = build_query_params(sortBy="status", sortOrder="asc")
        assert params["sortBy"] == "status"
        assert params["sortOrder"] == "asc"

    def test_kwargs_none_excluded(self):
        params = build_query_params(sortBy=None)
        assert "sortBy" not in params

    def test_kwargs_empty_string_excluded(self):
        params = build_query_params(sortBy="")
        assert "sortBy" not in params

    def test_all_params_combined(self):
        params = build_query_params(
            search="test",
            filter="active",
            q="query",
            after="cursor",
            limit=25,
            since="2024-01-01T00:00:00Z",
            until="2024-12-31T00:00:00Z",
        )
        assert len(params) == 7

    def test_empty_search_excluded(self):
        params = build_query_params(search="")
        assert "search" not in params
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_pagination_utils.py -v`
Expected: All 27 tests PASS

**Step 3: Commit**

```bash
git add tests/test_pagination_utils.py
git commit -m "test: add comprehensive tests for pagination utilities"
```

---

### Task 5: Expand Client Tests

**Files:**
- Modify: `tests/test_client.py`
- Source: `src/okta_mcp_server/utils/client.py`

**Step 1: Add additional edge case tests to `test_client.py`**

Append these tests to the existing `TestGetOktaClient` class:

```python
    @pytest.mark.asyncio
    async def test_reauthenticates_on_expired_token(self, monkeypatch):
        """get_okta_client should re-authenticate when token is expired."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=False)
            manager.authenticate = AsyncMock()

            # First call returns None (expired), second call returns new token
            with patch(
                "okta_mcp_server.utils.client.keyring.get_password",
                side_effect=[None, "new_token"],
            ):
                from okta_mcp_server.utils.client import get_okta_client

                client = await get_okta_client(manager)
                assert client is not None
                manager.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_after_reauth_still_no_token(self, monkeypatch):
        """get_okta_client should raise if token still None after re-authentication."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=False)
            manager.authenticate = AsyncMock()

            # Both calls return None
            with patch(
                "okta_mcp_server.utils.client.keyring.get_password",
                return_value=None,
            ):
                from okta_mcp_server.utils.client import get_okta_client

                with pytest.raises(RuntimeError, match="No API token available"):
                    await get_okta_client(manager)
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_client.py -v`
Expected: All 4 tests PASS

**Step 3: Commit**

```bash
git add tests/test_client.py
git commit -m "test: expand client utility tests with reauth edge cases"
```

---

### Task 6: Test Server Lifecycle

**Files:**
- Create: `tests/test_server.py`
- Source: `src/okta_mcp_server/server.py`

**Step 1: Write the tests**

```python
"""Tests for server lifecycle and initialization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from okta_mcp_server.server import OktaAppContext, okta_authorisation_flow


class TestOktaAppContext:
    """Tests for OktaAppContext dataclass."""

    def test_holds_auth_manager(self):
        mock_manager = MagicMock()
        ctx = OktaAppContext(okta_auth_manager=mock_manager)
        assert ctx.okta_auth_manager is mock_manager


class TestOktaAuthorisationFlow:
    """Tests for the lifespan context manager."""

    @pytest.mark.asyncio
    async def test_yields_context_with_manager(self):
        """Lifespan should authenticate and yield OktaAppContext."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            async with okta_authorisation_flow(mock_server) as ctx:
                assert isinstance(ctx, OktaAppContext)
                assert ctx.okta_auth_manager is mock_manager
                mock_manager.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_clears_tokens_on_exit(self):
        """Lifespan should clear tokens when context exits normally."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            async with okta_authorisation_flow(mock_server) as ctx:
                pass
            mock_manager.clear_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_clears_tokens_on_exception(self):
        """Lifespan should clear tokens even if an exception occurs."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            with pytest.raises(RuntimeError):
                async with okta_authorisation_flow(mock_server) as ctx:
                    raise RuntimeError("tool failure")
            mock_manager.clear_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_propagates_auth_failure(self):
        """Lifespan should propagate authentication failures."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock(side_effect=RuntimeError("Auth failed"))

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            with pytest.raises(RuntimeError, match="Auth failed"):
                async with okta_authorisation_flow(mock_server) as ctx:
                    pass
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/test_server.py -v`
Expected: All 5 tests PASS

**Step 3: Commit**

```bash
git add tests/test_server.py
git commit -m "test: add server lifecycle tests"
```

---

## Dependency Graph

All tasks are independent — each creates or modifies a separate test file for a separate source module. They can all be executed in parallel.

```
Task 1 (response)  ─┐
Task 2 (validators) ─┤
Task 3 (retry)      ─┤── All independent, can run in parallel
Task 4 (pagination) ─┤
Task 5 (client)     ─┤
Task 6 (server)     ─┘
```

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Utility test coverage | 11% (2/19 functions) | ~100% (19/19 functions) |
| New test files | 0 | 4 (response, validators, retry, pagination_utils, server) |
| Expanded test files | 0 | 1 (test_client.py) |
| Estimated new tests | 0 | ~105 |
| Total tests | 287 | ~392 |
