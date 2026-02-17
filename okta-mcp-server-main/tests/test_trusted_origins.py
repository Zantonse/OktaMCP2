# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for trusted origins management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListTrustedOrigins:
    """Tests for list_trusted_origins tool."""

    @pytest.mark.asyncio
    async def test_list_trusted_origins_success(self, mock_context, mock_okta_client):
        """Test successful trusted origins listing."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import list_trusted_origins

            result = await list_trusted_origins(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_trusted_origins_with_query(self, mock_context, mock_okta_client):
        """Test trusted origins listing with search query."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import list_trusted_origins

            result = await list_trusted_origins(ctx=mock_context, q="test")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_trusted_origins_with_limit(self, mock_context, mock_okta_client):
        """Test trusted origins listing with limit parameter."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import list_trusted_origins

            result = await list_trusted_origins(ctx=mock_context, limit=50)

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_trusted_origins_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import list_trusted_origins

            # Test with limit below minimum
            result = await list_trusted_origins(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetTrustedOrigin:
    """Tests for get_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_get_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin retrieval."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import get_trusted_origin

            result = await get_trusted_origin(origin_id="tos1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_trusted_origin_error_handling(self, mock_context):
        """Test error handling when trusted origin not found."""
        mock_client = AsyncMock()
        mock_client.get_trusted_origin = AsyncMock(side_effect=Exception("Trusted origin not found"))

        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import get_trusted_origin

            result = await get_trusted_origin(origin_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateTrustedOrigin:
    """Tests for create_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_create_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin creation."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import create_trusted_origin

            result = await create_trusted_origin(ctx=mock_context, name="Test Origin", origin="https://example.com")

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_trusted_origin_with_scopes(self, mock_context, mock_okta_client):
        """Test trusted origin creation with custom scopes."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import create_trusted_origin

            scopes = [{"type": "CORS"}]
            result = await create_trusted_origin(
                ctx=mock_context, name="Test Origin", origin="https://example.com", scopes=scopes
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_trusted_origin_default_scopes(self, mock_context, mock_okta_client):
        """Test trusted origin creation with default scopes."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import create_trusted_origin

            result = await create_trusted_origin(ctx=mock_context, name="Test Origin", origin="https://example.com")

            assert result.get("success") is True
            assert result.get("data") is not None


class TestUpdateTrustedOrigin:
    """Tests for update_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_update_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin update."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import update_trusted_origin

            result = await update_trusted_origin(origin_id="tos1abc123def456", ctx=mock_context, name="Updated Origin")

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_trusted_origin_with_scopes(self, mock_context, mock_okta_client):
        """Test trusted origin update with scopes."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import update_trusted_origin

            scopes = [{"type": "REDIRECT"}]
            result = await update_trusted_origin(
                origin_id="tos1abc123def456", ctx=mock_context, name="Updated Origin", scopes=scopes
            )

            assert result.get("success") is True


class TestDeleteTrustedOrigin:
    """Tests for delete_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_delete_trusted_origin_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_trusted_origin returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import delete_trusted_origin

            result = delete_trusted_origin(origin_id="tos1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True


class TestConfirmDeleteTrustedOrigin:
    """Tests for confirm_delete_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import confirm_delete_trusted_origin

            result = await confirm_delete_trusted_origin(
                origin_id="tos1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_trusted_origin_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import confirm_delete_trusted_origin

            result = await confirm_delete_trusted_origin(
                origin_id="tos1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateTrustedOrigin:
    """Tests for activate_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_activate_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin activation."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import activate_trusted_origin

            result = await activate_trusted_origin(origin_id="tos1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestDeactivateTrustedOrigin:
    """Tests for deactivate_trusted_origin tool."""

    @pytest.mark.asyncio
    async def test_deactivate_trusted_origin_success(self, mock_context, mock_okta_client):
        """Test successful trusted origin deactivation."""
        with patch(
            "okta_mcp_server.tools.trusted_origins.trusted_origins.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.trusted_origins.trusted_origins import deactivate_trusted_origin

            result = await deactivate_trusted_origin(origin_id="tos1abc123def456", ctx=mock_context)

            assert result.get("success") is True
