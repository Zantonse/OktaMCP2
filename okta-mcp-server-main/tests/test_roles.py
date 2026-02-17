# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for roles management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListRoles:
    """Tests for list_roles tool."""

    def test_list_roles_success(self, mock_context):
        """Test successful role types listing."""
        from okta_mcp_server.tools.roles.roles import list_roles

        result = list_roles(ctx=mock_context)

        assert result.get("success") is True
        assert "data" in result
        assert len(result.get("data", [])) > 0


class TestListUserRoles:
    """Tests for list_user_roles tool."""

    @pytest.mark.asyncio
    async def test_list_user_roles_success(self, mock_context, mock_okta_client):
        """Test successful user roles listing."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_user_roles

            result = await list_user_roles(user_id="00u1abc123", ctx=mock_context)

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_user_roles_error_handling(self, mock_context):
        """Test error handling when listing user roles fails."""
        mock_client = AsyncMock()
        mock_client.list_assigned_roles_for_user = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_user_roles

            result = await list_user_roles(user_id="00u1abc123", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestListGroupRoles:
    """Tests for list_group_roles tool."""

    @pytest.mark.asyncio
    async def test_list_group_roles_success(self, mock_context, mock_okta_client):
        """Test successful group roles listing."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_group_roles

            result = await list_group_roles(group_id="00g1abc123", ctx=mock_context)

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_group_roles_error_handling(self, mock_context):
        """Test error handling when listing group roles fails."""
        mock_client = AsyncMock()
        mock_client.list_assigned_roles_for_group = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_group_roles

            result = await list_group_roles(group_id="00g1abc123", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestAssignRoleToUser:
    """Tests for assign_role_to_user tool."""

    @pytest.mark.asyncio
    async def test_assign_role_to_user_success(self, mock_context, mock_okta_client):
        """Test successful role assignment to user."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import assign_role_to_user

            result = await assign_role_to_user(
                user_id="00u1abc123",
                role_type="USER_ADMIN",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_assign_role_to_user_error_handling(self, mock_context):
        """Test error handling when assigning role to user fails."""
        mock_client = AsyncMock()
        mock_client.assign_role_to_user = AsyncMock(side_effect=Exception("API error"))

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import assign_role_to_user

            result = await assign_role_to_user(
                user_id="00u1abc123",
                role_type="USER_ADMIN",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result


class TestUnassignRoleFromUser:
    """Tests for unassign_role_from_user tool."""

    @pytest.mark.asyncio
    async def test_unassign_role_from_user_success(self, mock_context, mock_okta_client):
        """Test successful role unassignment from user."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import unassign_role_from_user

            result = await unassign_role_from_user(
                user_id="00u1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_unassign_role_from_user_error_handling(self, mock_context):
        """Test error handling when unassigning role from user fails."""
        mock_client = AsyncMock()
        mock_client.unassign_role_from_user = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import unassign_role_from_user

            result = await unassign_role_from_user(
                user_id="00u1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result


class TestAssignRoleToGroup:
    """Tests for assign_role_to_group tool."""

    @pytest.mark.asyncio
    async def test_assign_role_to_group_success(self, mock_context, mock_okta_client):
        """Test successful role assignment to group."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import assign_role_to_group

            result = await assign_role_to_group(
                group_id="00g1abc123",
                role_type="USER_ADMIN",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_assign_role_to_group_error_handling(self, mock_context):
        """Test error handling when assigning role to group fails."""
        mock_client = AsyncMock()
        mock_client.assign_role_to_group = AsyncMock(side_effect=Exception("API error"))

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import assign_role_to_group

            result = await assign_role_to_group(
                group_id="00g1abc123",
                role_type="USER_ADMIN",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result


class TestUnassignRoleFromGroup:
    """Tests for unassign_role_from_group tool."""

    @pytest.mark.asyncio
    async def test_unassign_role_from_group_success(self, mock_context, mock_okta_client):
        """Test successful role unassignment from group."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import unassign_role_from_group

            result = await unassign_role_from_group(
                group_id="00g1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_unassign_role_from_group_error_handling(self, mock_context):
        """Test error handling when unassigning role from group fails."""
        mock_client = AsyncMock()
        mock_client.unassign_role_from_group = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import unassign_role_from_group

            result = await unassign_role_from_group(
                group_id="00g1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result


class TestListUserRoleTargets:
    """Tests for list_user_role_targets tool."""

    @pytest.mark.asyncio
    async def test_list_user_role_targets_group_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful listing of group targets for user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_user_role_targets

            result = await list_user_role_targets(
                user_id="00u1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
                target_type="GROUP",
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_user_role_targets_app_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful listing of app targets for user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_user_role_targets

            result = await list_user_role_targets(
                user_id="00u1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
                target_type="APP",
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_list_user_role_targets_error_handling(self, mock_context):
        """Test error handling when listing role targets fails."""
        mock_client = AsyncMock()
        mock_client.list_group_targets_for_role = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import list_user_role_targets

            result = await list_user_role_targets(
                user_id="00u1abc123",
                role_id="rol1abc123",
                ctx=mock_context,
                target_type="GROUP",
            )

            assert result.get("success") is False
            assert "error" in result


class TestAddUserRoleTarget:
    """Tests for add_user_role_target tool."""

    @pytest.mark.asyncio
    async def test_add_user_role_target_group_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful addition of group target to user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import add_user_role_target

            result = await add_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="GROUP",
                target_id="00g1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_add_user_role_target_app_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful addition of app target to user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import add_user_role_target

            result = await add_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="APP",
                target_id="0oa1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_add_user_role_target_error_handling(self, mock_context):
        """Test error handling when adding role target fails."""
        mock_client = AsyncMock()
        mock_client.add_group_target_to_role = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import add_user_role_target

            result = await add_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="GROUP",
                target_id="00g1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result


class TestRemoveUserRoleTarget:
    """Tests for remove_user_role_target tool."""

    @pytest.mark.asyncio
    async def test_remove_user_role_target_group_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful removal of group target from user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import remove_user_role_target

            result = await remove_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="GROUP",
                target_id="00g1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_remove_user_role_target_app_success(
        self, mock_context, mock_okta_client
    ):
        """Test successful removal of app target from user role."""
        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.roles.roles import remove_user_role_target

            result = await remove_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="APP",
                target_id="0oa1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_remove_user_role_target_error_handling(self, mock_context):
        """Test error handling when removing role target fails."""
        mock_client = AsyncMock()
        mock_client.remove_group_target_from_role = AsyncMock(
            side_effect=Exception("API error")
        )

        with patch(
            "okta_mcp_server.tools.roles.roles.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.roles.roles import remove_user_role_target

            result = await remove_user_role_target(
                user_id="00u1abc123",
                role_id="rol1abc123",
                target_type="GROUP",
                target_id="00g1abc123",
                ctx=mock_context,
            )

            assert result.get("success") is False
            assert "error" in result
