# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for authorization server management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListAuthorizationServers:
    """Tests for list_authorization_servers tool."""

    @pytest.mark.asyncio
    async def test_list_authorization_servers_success(self, mock_context, mock_okta_client):
        """Test successful authorization servers listing."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_authorization_servers

            result = await list_authorization_servers(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_authorization_servers_with_query(self, mock_context, mock_okta_client):
        """Test authorization servers listing with search query."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_authorization_servers

            result = await list_authorization_servers(ctx=mock_context, q="test")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_authorization_servers_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_authorization_servers

            # Test with limit below minimum
            result = await list_authorization_servers(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetAuthorizationServer:
    """Tests for get_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_get_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server retrieval."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import get_authorization_server

            result = await get_authorization_server(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_authorization_server_error_handling(self, mock_context):
        """Test error handling when authorization server not found."""
        mock_client = AsyncMock()
        mock_client.get_authorization_server = AsyncMock(side_effect=Exception("Authorization server not found"))

        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import get_authorization_server

            result = await get_authorization_server(auth_server_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateAuthorizationServer:
    """Tests for create_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_create_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server creation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_authorization_server

            result = await create_authorization_server(
                ctx=mock_context, name="Test Server", description="A test authorization server"
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_authorization_server_with_audiences(self, mock_context, mock_okta_client):
        """Test authorization server creation with audiences."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_authorization_server

            audiences = ["api://default", "api://custom"]
            result = await create_authorization_server(ctx=mock_context, name="Test Server", audiences=audiences)

            assert result.get("success") is True


class TestUpdateAuthorizationServer:
    """Tests for update_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_update_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server update."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import update_authorization_server

            result = await update_authorization_server(
                auth_server_id="aus1abc123def456", ctx=mock_context, name="Updated Server"
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_authorization_server_multiple_fields(self, mock_context, mock_okta_client):
        """Test authorization server update with multiple fields."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import update_authorization_server

            result = await update_authorization_server(
                auth_server_id="aus1abc123def456",
                ctx=mock_context,
                name="Updated Server",
                description="Updated description",
                audiences=["api://updated"],
            )

            assert result.get("success") is True


class TestDeleteAuthorizationServer:
    """Tests for delete_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_delete_authorization_server_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_authorization_server returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import delete_authorization_server

            result = delete_authorization_server(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True


class TestConfirmDeleteAuthorizationServer:
    """Tests for confirm_delete_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import confirm_delete_authorization_server

            result = await confirm_delete_authorization_server(
                auth_server_id="aus1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_authorization_server_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import confirm_delete_authorization_server

            result = await confirm_delete_authorization_server(
                auth_server_id="aus1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateAuthorizationServer:
    """Tests for activate_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_activate_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server activation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import activate_authorization_server

            result = await activate_authorization_server(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestDeactivateAuthorizationServer:
    """Tests for deactivate_authorization_server tool."""

    @pytest.mark.asyncio
    async def test_deactivate_authorization_server_success(self, mock_context, mock_okta_client):
        """Test successful authorization server deactivation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import deactivate_authorization_server

            result = await deactivate_authorization_server(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestListAuthServerPolicies:
    """Tests for list_auth_server_policies tool."""

    @pytest.mark.asyncio
    async def test_list_auth_server_policies_success(self, mock_context, mock_okta_client):
        """Test successful listing of authorization server policies."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_policies

            result = await list_auth_server_policies(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_auth_server_policies_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated for authorization server policies."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_policies

            result = await list_auth_server_policies(auth_server_id="aus1abc123def456", ctx=mock_context, limit=5)

            assert "items" in result


class TestCreateAuthServerPolicy:
    """Tests for create_auth_server_policy tool."""

    @pytest.mark.asyncio
    async def test_create_auth_server_policy_success(self, mock_context, mock_okta_client):
        """Test successful authorization server policy creation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_auth_server_policy

            policy_config = {
                "type": "OAUTH_AUTHORIZATION_POLICY",
                "status": "ACTIVE",
                "name": "Test Policy",
                "description": "Test policy description",
            }
            result = await create_auth_server_policy(
                auth_server_id="aus1abc123def456", ctx=mock_context, policy_config=policy_config
            )

            assert result.get("success") is True
            assert result.get("data") is not None


class TestListAuthServerScopes:
    """Tests for list_auth_server_scopes tool."""

    @pytest.mark.asyncio
    async def test_list_auth_server_scopes_success(self, mock_context, mock_okta_client):
        """Test successful listing of authorization server scopes."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_scopes

            result = await list_auth_server_scopes(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_auth_server_scopes_with_fetch_all(self, mock_context, mock_okta_client):
        """Test listing authorization server scopes with fetch_all parameter."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_scopes

            result = await list_auth_server_scopes(auth_server_id="aus1abc123def456", ctx=mock_context, fetch_all=True)

            assert "items" in result


class TestCreateAuthServerScope:
    """Tests for create_auth_server_scope tool."""

    @pytest.mark.asyncio
    async def test_create_auth_server_scope_success(self, mock_context, mock_okta_client):
        """Test successful authorization server scope creation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_auth_server_scope

            result = await create_auth_server_scope(
                auth_server_id="aus1abc123def456", ctx=mock_context, name="test_scope", description="Test scope"
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_auth_server_scope_with_display_name(self, mock_context, mock_okta_client):
        """Test authorization server scope creation with display name."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_auth_server_scope

            result = await create_auth_server_scope(
                auth_server_id="aus1abc123def456", ctx=mock_context, name="test_scope", display_name="Test Scope"
            )

            assert result.get("success") is True


class TestListAuthServerClaims:
    """Tests for list_auth_server_claims tool."""

    @pytest.mark.asyncio
    async def test_list_auth_server_claims_success(self, mock_context, mock_okta_client):
        """Test successful listing of authorization server claims."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_claims

            result = await list_auth_server_claims(auth_server_id="aus1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_auth_server_claims_with_limit(self, mock_context, mock_okta_client):
        """Test listing authorization server claims with custom limit."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import list_auth_server_claims

            result = await list_auth_server_claims(auth_server_id="aus1abc123def456", ctx=mock_context, limit=50)

            assert "items" in result


class TestCreateAuthServerClaim:
    """Tests for create_auth_server_claim tool."""

    @pytest.mark.asyncio
    async def test_create_auth_server_claim_success(self, mock_context, mock_okta_client):
        """Test successful authorization server claim creation."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_auth_server_claim

            result = await create_auth_server_claim(
                auth_server_id="aus1abc123def456",
                ctx=mock_context,
                name="test_claim",
                claim_type="RESOURCE",
                value_type="EXPRESSION",
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_auth_server_claim_with_value(self, mock_context, mock_okta_client):
        """Test authorization server claim creation with value."""
        with patch(
            "okta_mcp_server.tools.auth_servers.auth_servers.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.auth_servers.auth_servers import create_auth_server_claim

            result = await create_auth_server_claim(
                auth_server_id="aus1abc123def456",
                ctx=mock_context,
                name="test_claim",
                claim_type="IDENTITY",
                value_type="GROUPS",
                value="user.groups",
                alwaysInclude=True,
            )

            assert result.get("success") is True
