# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for identity provider management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListIdentityProviders:
    """Tests for list_identity_providers tool."""

    @pytest.mark.asyncio
    async def test_list_identity_providers_success(self, mock_context, mock_okta_client):
        """Test successful identity providers listing."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import list_identity_providers

            result = await list_identity_providers(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_identity_providers_with_query(self, mock_context, mock_okta_client):
        """Test identity providers listing with search query."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import list_identity_providers

            result = await list_identity_providers(ctx=mock_context, q="test")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_identity_providers_with_type_filter(self, mock_context, mock_okta_client):
        """Test identity providers listing with type filter."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import list_identity_providers

            result = await list_identity_providers(ctx=mock_context, type_filter="SAML2")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_identity_providers_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import list_identity_providers

            # Test with limit below minimum
            result = await list_identity_providers(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetIdentityProvider:
    """Tests for get_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_get_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider retrieval."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import get_identity_provider

            result = await get_identity_provider(idp_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_identity_provider_error_handling(self, mock_context):
        """Test error handling when identity provider not found."""
        mock_client = AsyncMock()
        mock_client.get_identity_provider = AsyncMock(side_effect=Exception("Identity provider not found"))

        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import get_identity_provider

            result = await get_identity_provider(idp_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateIdentityProvider:
    """Tests for create_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_create_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider creation."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import create_identity_provider

            result = await create_identity_provider(ctx=mock_context, name="Test IdP", idp_type="SAML2")

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_identity_provider_with_protocol(self, mock_context, mock_okta_client):
        """Test identity provider creation with protocol configuration."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import create_identity_provider

            protocol = {"type": "SAML2", "endpoints": {"sso": {"binding": "POST"}}}
            result = await create_identity_provider(
                ctx=mock_context, name="Test IdP", idp_type="SAML2", protocol=protocol
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_identity_provider_with_policy(self, mock_context, mock_okta_client):
        """Test identity provider creation with policy configuration."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import create_identity_provider

            policy = {"provisioning": {"action": "AUTO"}}
            result = await create_identity_provider(ctx=mock_context, name="Test IdP", idp_type="SAML2", policy=policy)

            assert result.get("success") is True


class TestUpdateIdentityProvider:
    """Tests for update_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_update_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider update."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import update_identity_provider

            result = await update_identity_provider(idp_id="0oa1abc123def456", ctx=mock_context, name="Updated IdP")

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_identity_provider_multiple_fields(self, mock_context, mock_okta_client):
        """Test identity provider update with multiple fields."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import update_identity_provider

            policy = {"provisioning": {"action": "AUTO"}}
            result = await update_identity_provider(
                idp_id="0oa1abc123def456", ctx=mock_context, name="Updated IdP", policy=policy
            )

            assert result.get("success") is True


class TestDeleteIdentityProvider:
    """Tests for delete_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_delete_identity_provider_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_identity_provider returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import delete_identity_provider

            result = delete_identity_provider(idp_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True


class TestConfirmDeleteIdentityProvider:
    """Tests for confirm_delete_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import confirm_delete_identity_provider

            result = await confirm_delete_identity_provider(
                idp_id="0oa1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_identity_provider_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import confirm_delete_identity_provider

            result = await confirm_delete_identity_provider(
                idp_id="0oa1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateIdentityProvider:
    """Tests for activate_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_activate_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider activation."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import activate_identity_provider

            result = await activate_identity_provider(idp_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestDeactivateIdentityProvider:
    """Tests for deactivate_identity_provider tool."""

    @pytest.mark.asyncio
    async def test_deactivate_identity_provider_success(self, mock_context, mock_okta_client):
        """Test successful identity provider deactivation."""
        with patch(
            "okta_mcp_server.tools.identity_providers.identity_providers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.identity_providers.identity_providers import deactivate_identity_provider

            result = await deactivate_identity_provider(idp_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True
