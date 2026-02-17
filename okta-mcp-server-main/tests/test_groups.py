# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for group management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListGroups:
    """Tests for list_groups tool."""

    @pytest.mark.asyncio
    async def test_list_groups_success(self, mock_context, mock_okta_client):
        """Test successful group listing."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import list_groups

            result = await list_groups(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_groups_with_search(self, mock_context, mock_okta_client):
        """Test group listing with search parameter."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import list_groups

            result = await list_groups(
                ctx=mock_context,
                search='profile.name sw "Test"',
            )

            assert "items" in result


class TestGetGroup:
    """Tests for get_group tool."""

    @pytest.mark.asyncio
    async def test_get_group_success(self, mock_context, mock_okta_client):
        """Test successful group retrieval."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import get_group

            result = await get_group(group_id="00g1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None


class TestCreateGroup:
    """Tests for create_group tool."""

    @pytest.mark.asyncio
    async def test_create_group_success(self, mock_context, mock_okta_client):
        """Test successful group creation."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import create_group

            profile = {
                "name": "New Group",
                "description": "A new test group",
            }

            result = await create_group(profile=profile, ctx=mock_context)

            assert result.get("success") is True


class TestUpdateGroup:
    """Tests for update_group tool."""

    @pytest.mark.asyncio
    async def test_update_group_success(self, mock_context, mock_okta_client):
        """Test successful group update."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import update_group

            result = await update_group(
                group_id="00g1abc123def456",
                profile={"name": "Updated Group"},
                ctx=mock_context,
            )

            assert result.get("success") is True


class TestDeleteGroup:
    """Tests for delete_group and confirm_delete_group tools."""

    @pytest.mark.asyncio
    async def test_delete_group_returns_confirmation(self, mock_context):
        """Test that delete_group returns confirmation request."""
        from okta_mcp_server.tools.groups.groups import delete_group

        result = await delete_group(group_id="00g1abc123def456", ctx=mock_context)

        assert result.get("success") is True
        assert result.get("data", {}).get("confirmation_required") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_group_success(self, mock_context, mock_okta_client):
        """Test successful group deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import confirm_delete_group

            result = await confirm_delete_group(
                group_id="00g1abc123def456",
                confirmation="DELETE",
                ctx=mock_context,
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_group_wrong_confirmation(self, mock_context):
        """Test that wrong confirmation cancels deletion."""
        from okta_mcp_server.tools.groups.groups import confirm_delete_group

        result = await confirm_delete_group(
            group_id="00g1abc123def456",
            confirmation="WRONG",
            ctx=mock_context,
        )

        assert result.get("success") is False
        assert "cancelled" in result.get("error", "").lower()


class TestListGroupUsers:
    """Tests for list_group_users tool."""

    @pytest.mark.asyncio
    async def test_list_group_users_success(self, mock_context, mock_okta_client):
        """Test successful listing of group users."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import list_group_users

            result = await list_group_users(group_id="00g1abc123def456", ctx=mock_context)

            assert "items" in result


class TestGroupMembership:
    """Tests for add_user_to_group and remove_user_from_group tools."""

    @pytest.mark.asyncio
    async def test_add_user_to_group_success(self, mock_context, mock_okta_client):
        """Test successful adding user to group."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import add_user_to_group

            result = await add_user_to_group(
                group_id="00g1abc123def456",
                user_id="00u1abc123def456",
                ctx=mock_context,
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_remove_user_from_group_success(self, mock_context, mock_okta_client):
        """Test successful removing user from group."""
        with patch(
            "okta_mcp_server.tools.groups.groups.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.groups.groups import remove_user_from_group

            result = await remove_user_from_group(
                group_id="00g1abc123def456",
                user_id="00u1abc123def456",
                ctx=mock_context,
            )

            assert result.get("success") is True
