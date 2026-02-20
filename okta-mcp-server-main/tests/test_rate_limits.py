# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta rate limits management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetRateLimitSettings:
    """Tests for get_rate_limit_settings function."""

    @pytest.mark.asyncio
    async def test_get_rate_limit_settings_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving rate limit settings."""
        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import get_rate_limit_settings

            result = await get_rate_limit_settings(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_rate_limit_settings_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.get_rate_limit_settings_admin_notifications = AsyncMock(
            return_value=(None, None, "Okta API error")
        )

        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import get_rate_limit_settings

            result = await get_rate_limit_settings(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetPerClientRateLimit:
    """Tests for get_per_client_rate_limit function."""

    @pytest.mark.asyncio
    async def test_get_per_client_rate_limit_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving per-client rate limit settings."""
        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import get_per_client_rate_limit

            result = await get_per_client_rate_limit(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_per_client_rate_limit_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.get_per_client_rate_limit_settings = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import get_per_client_rate_limit

            result = await get_per_client_rate_limit(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdatePerClientRateLimit:
    """Tests for update_per_client_rate_limit function."""

    @pytest.mark.asyncio
    async def test_update_per_client_rate_limit_success(self, mock_context, mock_okta_client):
        """Test successfully updating per-client rate limit settings."""
        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import update_per_client_rate_limit

            result = await update_per_client_rate_limit(
                ctx=mock_context, settings={"default_mode": "ENFORCED", "use_dynamic_enforcement": True}
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_per_client_rate_limit_empty_dict(self, mock_context):
        """Test error handling with empty settings dictionary."""
        from okta_mcp_server.tools.rate_limits.rate_limits import update_per_client_rate_limit

        result = await update_per_client_rate_limit(ctx=mock_context, settings={})
        assert result.get("success") is False
        assert "error" in result
        assert "non-empty dictionary" in result.get("error")

    @pytest.mark.asyncio
    async def test_update_per_client_rate_limit_non_dict(self, mock_context):
        """Test error handling with non-dict settings."""
        from okta_mcp_server.tools.rate_limits.rate_limits import update_per_client_rate_limit

        result = await update_per_client_rate_limit(ctx=mock_context, settings="invalid")
        assert result.get("success") is False
        assert "error" in result
        assert "non-empty dictionary" in result.get("error")

    @pytest.mark.asyncio
    async def test_update_per_client_rate_limit_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.replace_per_client_rate_limit_settings = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.rate_limits.rate_limits.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.rate_limits.rate_limits import update_per_client_rate_limit

            result = await update_per_client_rate_limit(ctx=mock_context, settings={"default_mode": "ENFORCED"})
            assert result.get("success") is False
            assert "error" in result
