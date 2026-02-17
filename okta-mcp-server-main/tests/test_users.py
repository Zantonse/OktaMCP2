# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for user management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListUsers:
    """Tests for list_users tool."""

    @pytest.mark.asyncio
    async def test_list_users_success(self, mock_context, mock_okta_client):
        """Test successful user listing."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_users_with_search(self, mock_context, mock_okta_client):
        """Test user listing with search parameter."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(
                ctx=mock_context,
                search='profile.email eq "test@example.com"',
            )

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_users_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_users

            # Test with limit below minimum
            result = await list_users(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetUser:
    """Tests for get_user tool."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, mock_context, mock_okta_client):
        """Test successful user retrieval."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import get_user

            result = await get_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_user_error_handling(self, mock_context):
        """Test error handling when user not found."""
        mock_client = AsyncMock()
        mock_client.get_user = AsyncMock(side_effect=Exception("User not found"))

        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.users.users import get_user

            result = await get_user(user_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateUser:
    """Tests for create_user tool."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_context, mock_okta_client):
        """Test successful user creation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import create_user

            profile = {
                "firstName": "New",
                "lastName": "User",
                "email": "new@example.com",
                "login": "new@example.com",
            }

            result = await create_user(profile=profile, ctx=mock_context)

            assert result.get("success") is True


class TestUpdateUser:
    """Tests for update_user tool."""

    @pytest.mark.asyncio
    async def test_update_user_success(self, mock_context, mock_okta_client):
        """Test successful user update."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import update_user

            result = await update_user(
                user_id="00u1abc123def456",
                profile={"firstName": "Updated"},
                ctx=mock_context,
            )

            assert result.get("success") is True


class TestDeactivateUser:
    """Tests for deactivate_user tool."""

    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, mock_context, mock_okta_client):
        """Test successful user deactivation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import deactivate_user

            result = await deactivate_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "deactivated" in result.get("data", {}).get("message", "").lower()


class TestDeleteDeactivatedUser:
    """Tests for delete_deactivated_user tool."""

    @pytest.mark.asyncio
    async def test_delete_deactivated_user_success(self, mock_context, mock_okta_client):
        """Test successful deletion of deactivated user."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import delete_deactivated_user

            result = await delete_deactivated_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestActivateUser:
    """Tests for activate_user tool."""

    @pytest.mark.asyncio
    async def test_activate_user_success(self, mock_context, mock_okta_client):
        """Test successful user activation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import activate_user

            result = await activate_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "activated" in result.get("data", {}).get("message", "").lower()


class TestReactivateUser:
    """Tests for reactivate_user tool."""

    @pytest.mark.asyncio
    async def test_reactivate_user_success(self, mock_context, mock_okta_client):
        """Test successful user reactivation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import reactivate_user

            result = await reactivate_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "reactivated" in result.get("data", {}).get("message", "").lower()


class TestSuspendUser:
    """Tests for suspend_user tool."""

    @pytest.mark.asyncio
    async def test_suspend_user_success(self, mock_context, mock_okta_client):
        """Test successful user suspension."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import suspend_user

            result = await suspend_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "suspended" in result.get("data", {}).get("message", "").lower()


class TestUnsuspendUser:
    """Tests for unsuspend_user tool."""

    @pytest.mark.asyncio
    async def test_unsuspend_user_success(self, mock_context, mock_okta_client):
        """Test successful user unsuspension."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import unsuspend_user

            result = await unsuspend_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "unsuspended" in result.get("data", {}).get("message", "").lower()


class TestUnlockUser:
    """Tests for unlock_user tool."""

    @pytest.mark.asyncio
    async def test_unlock_user_success(self, mock_context, mock_okta_client):
        """Test successful user unlock."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import unlock_user

            result = await unlock_user(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "unlocked" in result.get("data", {}).get("message", "").lower()


class TestExpirePassword:
    """Tests for expire_password tool."""

    @pytest.mark.asyncio
    async def test_expire_password_success(self, mock_context, mock_okta_client):
        """Test successful password expiration."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import expire_password

            result = await expire_password(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "expired" in result.get("data", {}).get("message", "").lower()


class TestExpirePasswordWithTempPassword:
    """Tests for expire_password_with_temp_password tool."""

    @pytest.mark.asyncio
    async def test_expire_password_with_temp_password_success(self, mock_context, mock_okta_client):
        """Test successful password expiration with temp password generation."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import expire_password_with_temp_password

            result = await expire_password_with_temp_password(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "temp_password" in result.get("data", {})
            assert result.get("data", {}).get("temp_password") is not None


class TestResetPassword:
    """Tests for reset_password tool."""

    @pytest.mark.asyncio
    async def test_reset_password_success(self, mock_context, mock_okta_client):
        """Test successful password reset."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import reset_password

            result = await reset_password(user_id="00u1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert "reset" in result.get("data", {}).get("message", "").lower()

    @pytest.mark.asyncio
    async def test_reset_password_without_email(self, mock_context, mock_okta_client):
        """Test password reset without sending email."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import reset_password

            result = await reset_password(user_id="00u1abc123def456", send_email=False, ctx=mock_context)

            assert result.get("success") is True


class TestListUserGroups:
    """Tests for list_user_groups tool."""

    @pytest.mark.asyncio
    async def test_list_user_groups_success(self, mock_context, mock_okta_client):
        """Test successful listing of user groups."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_user_groups

            result = await list_user_groups(user_id="00u1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_user_groups_with_limit(self, mock_context, mock_okta_client):
        """Test listing user groups with limit parameter."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_user_groups

            result = await list_user_groups(user_id="00u1abc123def456", limit=50, ctx=mock_context)

            assert "items" in result


class TestListUserApps:
    """Tests for list_user_apps tool."""

    @pytest.mark.asyncio
    async def test_list_user_apps_success(self, mock_context, mock_okta_client):
        """Test successful listing of user apps."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_user_apps

            result = await list_user_apps(user_id="00u1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_user_apps_with_limit(self, mock_context, mock_okta_client):
        """Test listing user apps with limit parameter."""
        with patch(
            "okta_mcp_server.tools.users.users.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.users.users import list_user_apps

            result = await list_user_apps(user_id="00u1abc123def456", limit=50, ctx=mock_context)

            assert "items" in result
