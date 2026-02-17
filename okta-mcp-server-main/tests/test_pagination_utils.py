# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

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
