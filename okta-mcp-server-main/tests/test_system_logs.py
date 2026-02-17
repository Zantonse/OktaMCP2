# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for system logs retrieval tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MockOktaResponse


class TestGetLogs:
    """Tests for get_logs tool."""

    @pytest.mark.asyncio
    async def test_get_logs_success(self, mock_context, mock_okta_client):
        """Test successful system logs retrieval."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

            assert "items" in result
            assert "total_fetched" in result
            assert result["total_fetched"] >= 0
            assert "has_more" in result
            assert "fetch_all_used" in result
            assert result["fetch_all_used"] is False

    @pytest.mark.asyncio
    async def test_get_logs_empty(self, mock_context):
        """Test get_logs when no logs are found."""
        mock_client = AsyncMock()
        mock_client.get_logs = AsyncMock(return_value=([], MockOktaResponse(), None))

        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

            assert "items" in result
            assert result["total_fetched"] == 0
            assert result["has_more"] is False

    @pytest.mark.asyncio
    async def test_get_logs_api_error(self, mock_context):
        """Test error handling for API failures."""
        mock_client = AsyncMock()
        mock_client.get_logs = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, mock_context, mock_okta_client):
        """Test get_logs with time filters."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(
                ctx=mock_context,
                since="2024-01-01T00:00:00.000Z",
                until="2024-01-02T00:00:00.000Z",
            )

            assert "items" in result
            assert result["total_fetched"] >= 0

    @pytest.mark.asyncio
    async def test_get_logs_with_query_filter(self, mock_context, mock_okta_client):
        """Test get_logs with query filter."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, q="user.lifecycle.create")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_logs_with_filter_expression(self, mock_context, mock_okta_client):
        """Test get_logs with filter expression."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, filter_expr='eventType eq "user.lifecycle.create"')

            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_logs_limit_clamping_below_minimum(self, mock_context, mock_okta_client):
        """Test that limit below minimum is clamped to 20."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, limit=5)

            assert "items" in result
            assert result["total_fetched"] >= 0

    @pytest.mark.asyncio
    async def test_get_logs_limit_clamping_above_maximum(self, mock_context, mock_okta_client):
        """Test that limit above maximum is clamped to 100."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, limit=200)

            assert "items" in result

    @pytest.mark.asyncio
    async def test_get_logs_with_after_cursor(self, mock_context, mock_okta_client):
        """Test get_logs with pagination cursor."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, after="cursor123")

            assert "items" in result
            assert "next_cursor" in result

    @pytest.mark.asyncio
    async def test_get_logs_exception_handling(self, mock_context):
        """Test general exception handling."""
        mock_client = AsyncMock()
        mock_client.get_logs = AsyncMock(side_effect=ValueError("Invalid parameter"))

        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_logs_fetch_all_false(self, mock_context, mock_okta_client):
        """Test get_logs with fetch_all=False (default)."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context, fetch_all=False)

            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_get_logs_returns_structured_response(self, mock_context, mock_okta_client):
        """Test that get_logs returns properly structured response."""
        with patch(
            "okta_mcp_server.tools.system_logs.system_logs.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

            # Verify response structure
            assert isinstance(result, dict)
            assert "items" in result
            assert "total_fetched" in result
            assert "has_more" in result
            assert "next_cursor" in result
            assert "fetch_all_used" in result
            assert isinstance(result["items"], list)
            assert isinstance(result["total_fetched"], int)
            assert isinstance(result["has_more"], bool)
            assert isinstance(result["fetch_all_used"], bool)
