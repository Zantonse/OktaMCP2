# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.  # noqa: E501
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  # noqa: E501
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for user type management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListUserTypes:
    @pytest.mark.asyncio
    async def test_list_user_types_success(self, mock_context, mock_okta_client):
        """Test successful listing of user types."""
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import list_user_types

            result = await list_user_types(ctx=mock_context)
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_list_user_types_api_error(self, mock_context, mock_okta_client):
        """Test list_user_types handles API errors."""
        mock_okta_client.list_user_types = AsyncMock(return_value=(None, None, "API Error"))
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import list_user_types

            result = await list_user_types(ctx=mock_context)
            assert result.get("success") is False


class TestGetUserType:
    @pytest.mark.asyncio
    async def test_get_user_type_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a user type."""
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import get_user_type

            result = await get_user_type(ctx=mock_context, type_id="oty1abc123def456")
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_get_user_type_invalid_id(self, mock_context):
        """Test get_user_type with invalid type_id."""
        from okta_mcp_server.tools.user_types.user_types import get_user_type

        result = await get_user_type(ctx=mock_context, type_id="invalid_id")
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_get_user_type_api_error(self, mock_context, mock_okta_client):
        """Test get_user_type handles API errors."""
        mock_okta_client.get_user_type = AsyncMock(return_value=(None, None, "API Error"))
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import get_user_type

            result = await get_user_type(ctx=mock_context, type_id="oty1abc123def456")
            assert result.get("success") is False


class TestCreateUserType:
    @pytest.mark.asyncio
    async def test_create_user_type_success(self, mock_context, mock_okta_client):
        """Test successful creation of a user type."""
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import create_user_type

            result = await create_user_type(
                ctx=mock_context,
                name="Engineer",
                display_name="Engineer User Type",
                description="A custom user type for engineers",
            )
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_user_type_api_error(self, mock_context, mock_okta_client):
        """Test create_user_type handles API errors."""
        mock_okta_client.create_user_type = AsyncMock(return_value=(None, None, "API Error"))
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import create_user_type

            result = await create_user_type(
                ctx=mock_context,
                name="Engineer",
                display_name="Engineer User Type",
                description="A custom user type for engineers",
            )
            assert result.get("success") is False


class TestUpdateUserType:
    @pytest.mark.asyncio
    async def test_update_user_type_success(self, mock_context, mock_okta_client):
        """Test successful update of a user type."""
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import update_user_type

            result = await update_user_type(
                ctx=mock_context,
                type_id="oty1abc123def456",
                display_name="Updated Display Name",
            )
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_user_type_invalid_id(self, mock_context):
        """Test update_user_type with invalid type_id."""
        from okta_mcp_server.tools.user_types.user_types import update_user_type

        result = await update_user_type(
            ctx=mock_context,
            type_id="invalid_id",
            display_name="Updated Display Name",
        )
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_update_user_type_api_error(self, mock_context, mock_okta_client):
        """Test update_user_type handles API errors."""
        mock_okta_client.update_user_type = AsyncMock(return_value=(None, None, "API Error"))
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import update_user_type

            result = await update_user_type(
                ctx=mock_context,
                type_id="oty1abc123def456",
                display_name="Updated Display Name",
            )
            assert result.get("success") is False


class TestDeleteUserType:
    def test_delete_user_type_returns_confirmation(self, mock_context):
        """Test that delete_user_type returns confirmation request."""
        from okta_mcp_server.tools.user_types.user_types import delete_user_type

        result = delete_user_type(ctx=mock_context, type_id="oty1abc123def456")
        assert result.get("success") is True
        assert result.get("data", {}).get("confirmation_required") is True

    def test_delete_user_type_invalid_id(self, mock_context):
        """Test delete_user_type with invalid type_id."""
        from okta_mcp_server.tools.user_types.user_types import delete_user_type

        result = delete_user_type(ctx=mock_context, type_id="invalid@id")
        assert result.get("success") is False


class TestConfirmDeleteUserType:
    @pytest.mark.asyncio
    async def test_confirm_delete_user_type_success(self, mock_context, mock_okta_client):
        """Test successful user type deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import confirm_delete_user_type

            result = await confirm_delete_user_type(
                ctx=mock_context,
                type_id="oty1abc123def456",
                confirmation="DELETE",
            )
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_user_type_wrong_confirmation(self, mock_context):
        """Test confirm_delete_user_type with wrong confirmation string."""
        from okta_mcp_server.tools.user_types.user_types import confirm_delete_user_type

        result = await confirm_delete_user_type(
            ctx=mock_context,
            type_id="oty1abc123def456",
            confirmation="WRONG",
        )
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_confirm_delete_user_type_invalid_id(self, mock_context):
        """Test confirm_delete_user_type with invalid type_id."""
        from okta_mcp_server.tools.user_types.user_types import confirm_delete_user_type

        result = await confirm_delete_user_type(
            ctx=mock_context,
            type_id="invalid_id",
            confirmation="DELETE",
        )
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_confirm_delete_user_type_api_error(self, mock_context, mock_okta_client):
        """Test confirm_delete_user_type handles API errors."""
        mock_okta_client.delete_user_type = AsyncMock(return_value=(None, "API Error"))
        with patch(
            "okta_mcp_server.tools.user_types.user_types.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.user_types.user_types import confirm_delete_user_type

            result = await confirm_delete_user_type(
                ctx=mock_context,
                type_id="oty1abc123def456",
                confirmation="DELETE",
            )
            assert result.get("success") is False
