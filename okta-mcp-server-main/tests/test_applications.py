# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for application management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListApplications:
    """Tests for list_applications tool."""

    @pytest.mark.asyncio
    async def test_list_applications_success(self, mock_context, mock_okta_client):
        """Test successful applications listing."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_applications

            result = await list_applications(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_applications_with_query(self, mock_context, mock_okta_client):
        """Test applications listing with search query."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_applications

            result = await list_applications(ctx=mock_context, q="test")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_applications_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_applications

            # Test with limit below minimum
            result = await list_applications(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetApplication:
    """Tests for get_application tool."""

    @pytest.mark.asyncio
    async def test_get_application_success(self, mock_context, mock_okta_client):
        """Test successful application retrieval."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application

            result = await get_application(app_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_application_error_handling(self, mock_context):
        """Test error handling when application not found."""
        mock_client = AsyncMock()
        mock_client.get_application = AsyncMock(side_effect=Exception("Application not found"))

        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application

            result = await get_application(app_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateApplication:
    """Tests for create_application tool."""

    @pytest.mark.asyncio
    async def test_create_application_success(self, mock_context, mock_okta_client):
        """Test successful application creation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import create_application

            app_config = {"name": "test_app", "label": "Test Application", "signOnMode": "SAML_2_0"}

            result = await create_application(ctx=mock_context, app_config=app_config)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_application_with_activate_false(self, mock_context, mock_okta_client):
        """Test application creation without activation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import create_application

            app_config = {"name": "test_app", "label": "Test Application"}

            result = await create_application(ctx=mock_context, app_config=app_config, activate=False)

            assert result.get("success") is True


class TestUpdateApplication:
    """Tests for update_application tool."""

    @pytest.mark.asyncio
    async def test_update_application_success(self, mock_context, mock_okta_client):
        """Test successful application update."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import update_application

            app_config = {"name": "updated_app", "label": "Updated Application"}

            result = await update_application(app_id="0oa1abc123def456", ctx=mock_context, app_config=app_config)

            assert result.get("success") is True


class TestDeleteApplication:
    """Tests for delete_application tool."""

    @pytest.mark.asyncio
    async def test_delete_application_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_application returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import delete_application

            result = delete_application(app_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True


class TestConfirmDeleteApplication:
    """Tests for confirm_delete_application tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_application_success(self, mock_context, mock_okta_client):
        """Test successful application deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import confirm_delete_application

            result = await confirm_delete_application(
                app_id="0oa1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_application_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import confirm_delete_application

            result = await confirm_delete_application(
                app_id="0oa1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateApplication:
    """Tests for activate_application tool."""

    @pytest.mark.asyncio
    async def test_activate_application_success(self, mock_context, mock_okta_client):
        """Test successful application activation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import activate_application

            result = await activate_application(app_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestDeactivateApplication:
    """Tests for deactivate_application tool."""

    @pytest.mark.asyncio
    async def test_deactivate_application_success(self, mock_context, mock_okta_client):
        """Test successful application deactivation."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import deactivate_application

            result = await deactivate_application(app_id="0oa1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestListApplicationUsers:
    """Tests for list_application_users tool."""

    @pytest.mark.asyncio
    async def test_list_application_users_success(self, mock_context, mock_okta_client):
        """Test successful listing of application users."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_application_users

            result = await list_application_users(app_id="0oa1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_application_users_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated for application users."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_application_users

            result = await list_application_users(app_id="0oa1abc123def456", ctx=mock_context, limit=5)

            assert "items" in result


class TestGetApplicationUser:
    """Tests for get_application_user tool."""

    @pytest.mark.asyncio
    async def test_get_application_user_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of application user."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application_user

            result = await get_application_user(
                app_id="0oa1abc123def456", user_id="00u1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_application_user_error_handling(self, mock_context):
        """Test error handling when application user not found."""
        mock_client = AsyncMock()
        mock_client.get_application_user = AsyncMock(side_effect=Exception("User not found in application"))

        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application_user

            result = await get_application_user(app_id="0oa1abc123def456", user_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestAssignUserToApplication:
    """Tests for assign_user_to_application tool."""

    @pytest.mark.asyncio
    async def test_assign_user_to_application_success(self, mock_context, mock_okta_client):
        """Test successful user assignment to application."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import assign_user_to_application

            result = await assign_user_to_application(
                app_id="0oa1abc123def456", user_id="00u1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_assign_user_to_application_with_config(self, mock_context, mock_okta_client):
        """Test user assignment with additional configuration."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import assign_user_to_application

            app_user_config = {"credentials": {"provider": {"id": "okta"}, "user": {"name": "user@example.com"}}}

            result = await assign_user_to_application(
                app_id="0oa1abc123def456",
                user_id="00u1abc123def456",
                ctx=mock_context,
                app_user_config=app_user_config,
            )

            assert result.get("success") is True


class TestRemoveUserFromApplication:
    """Tests for remove_user_from_application tool."""

    @pytest.mark.asyncio
    async def test_remove_user_from_application_success(self, mock_context, mock_okta_client):
        """Test successful removal of user from application."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import remove_user_from_application

            result = await remove_user_from_application(
                app_id="0oa1abc123def456", user_id="00u1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True


class TestListApplicationGroups:
    """Tests for list_application_groups tool."""

    @pytest.mark.asyncio
    async def test_list_application_groups_success(self, mock_context, mock_okta_client):
        """Test successful listing of application groups."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_application_groups

            result = await list_application_groups(app_id="0oa1abc123def456", ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_application_groups_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated for application groups."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import list_application_groups

            result = await list_application_groups(app_id="0oa1abc123def456", ctx=mock_context, limit=5)

            assert "items" in result


class TestGetApplicationGroup:
    """Tests for get_application_group tool."""

    @pytest.mark.asyncio
    async def test_get_application_group_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of application group."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application_group

            result = await get_application_group(
                app_id="0oa1abc123def456", group_id="00g1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_application_group_error_handling(self, mock_context):
        """Test error handling when application group not found."""
        mock_client = AsyncMock()
        mock_client.get_application_group_assignment = AsyncMock(
            side_effect=Exception("Group not found in application")
        )

        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.applications.applications import get_application_group

            result = await get_application_group(app_id="0oa1abc123def456", group_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestAssignGroupToApplication:
    """Tests for assign_group_to_application tool."""

    @pytest.mark.asyncio
    async def test_assign_group_to_application_success(self, mock_context, mock_okta_client):
        """Test successful group assignment to application."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import assign_group_to_application

            result = await assign_group_to_application(
                app_id="0oa1abc123def456", group_id="00g1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
            assert result.get("data") is not None


class TestRemoveGroupFromApplication:
    """Tests for remove_group_from_application tool."""

    @pytest.mark.asyncio
    async def test_remove_group_from_application_success(self, mock_context, mock_okta_client):
        """Test successful removal of group from application."""
        with patch(
            "okta_mcp_server.tools.applications.applications.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.applications.applications import remove_group_from_application

            result = await remove_group_from_application(
                app_id="0oa1abc123def456", group_id="00g1abc123def456", ctx=mock_context
            )

            assert result.get("success") is True
