# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta linked objects management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListLinkedObjectDefinitions:
    """Tests for list_linked_object_definitions function."""

    @pytest.mark.asyncio
    async def test_list_linked_object_definitions_success(self, mock_context, mock_okta_client):
        """Test successfully listing linked object definitions."""
        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import list_linked_object_definitions

            result = await list_linked_object_definitions(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_linked_object_definitions_error(self, mock_context):
        """Test error handling when listing linked object definitions fails."""
        mock_client = AsyncMock()
        mock_client.list_linked_object_definitions = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import list_linked_object_definitions

            result = await list_linked_object_definitions(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetLinkedObjectDefinition:
    """Tests for get_linked_object_definition function."""

    @pytest.mark.asyncio
    async def test_get_linked_object_definition_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a linked object definition."""
        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import get_linked_object_definition

            result = await get_linked_object_definition(ctx=mock_context, linked_object_name="manager")
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_linked_object_definition_empty_name(self, mock_context):
        """Test error handling when linked_object_name is empty."""
        from okta_mcp_server.tools.linked_objects.linked_objects import get_linked_object_definition

        result = await get_linked_object_definition(ctx=mock_context, linked_object_name="")
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_linked_object_definition_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.get_linked_object_definition = AsyncMock(return_value=(None, None, "Not found"))

        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import get_linked_object_definition

            result = await get_linked_object_definition(ctx=mock_context, linked_object_name="manager")
            assert result.get("success") is False
            assert "error" in result


class TestCreateLinkedObjectDefinition:
    """Tests for create_linked_object_definition function."""

    @pytest.mark.asyncio
    async def test_create_linked_object_definition_success(self, mock_context, mock_okta_client):
        """Test successfully creating a linked object definition."""
        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import create_linked_object_definition

            result = await create_linked_object_definition(
                ctx=mock_context,
                primary_name="manager",
                primary_title="Manager",
                primary_description="Manager relationship",
                associated_name="subordinate",
                associated_title="Subordinate",
                associated_description="Subordinate relationship",
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_create_linked_object_definition_api_error(self, mock_context):
        """Test error handling when creation fails."""
        mock_client = AsyncMock()
        mock_client.add_linked_object_definition = AsyncMock(return_value=(None, None, "Invalid request"))

        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import create_linked_object_definition

            result = await create_linked_object_definition(
                ctx=mock_context,
                primary_name="manager",
                primary_title="Manager",
                primary_description="Manager relationship",
                associated_name="subordinate",
                associated_title="Subordinate",
                associated_description="Subordinate relationship",
            )
            assert result.get("success") is False
            assert "error" in result


class TestDeleteLinkedObjectDefinition:
    """Tests for delete_linked_object_definition and confirm_delete_linked_object_definition functions."""

    def test_delete_linked_object_definition_success(self, mock_context):
        """Test successful deletion request (step 1)."""
        from okta_mcp_server.tools.linked_objects.linked_objects import delete_linked_object_definition

        result = delete_linked_object_definition(ctx=mock_context, linked_object_name="manager")
        assert result.get("success") is True
        assert result.get("data").get("confirmation_required") is True
        assert "DELETE" in result.get("data").get("message")

    def test_delete_linked_object_definition_empty_name(self, mock_context):
        """Test error handling when linked_object_name is empty."""
        from okta_mcp_server.tools.linked_objects.linked_objects import delete_linked_object_definition

        result = delete_linked_object_definition(ctx=mock_context, linked_object_name="")
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_linked_object_definition_success(self, mock_context, mock_okta_client):
        """Test successful deletion confirmation (step 2)."""
        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import confirm_delete_linked_object_definition

            result = await confirm_delete_linked_object_definition(
                ctx=mock_context, linked_object_name="manager", confirmation="DELETE"
            )
            assert result.get("success") is True
            assert "deleted successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_confirm_delete_linked_object_definition_wrong_confirmation(self, mock_context):
        """Test error handling with incorrect confirmation."""
        from okta_mcp_server.tools.linked_objects.linked_objects import confirm_delete_linked_object_definition

        result = await confirm_delete_linked_object_definition(
            ctx=mock_context, linked_object_name="manager", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_linked_object_definition_empty_name(self, mock_context):
        """Test error handling when linked_object_name is empty."""
        from okta_mcp_server.tools.linked_objects.linked_objects import confirm_delete_linked_object_definition

        result = await confirm_delete_linked_object_definition(
            ctx=mock_context, linked_object_name="", confirmation="DELETE"
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_linked_object_definition_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.delete_linked_object_definition = AsyncMock(return_value=(None, "API error"))

        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import confirm_delete_linked_object_definition

            result = await confirm_delete_linked_object_definition(
                ctx=mock_context, linked_object_name="manager", confirmation="DELETE"
            )
            assert result.get("success") is False
            assert "error" in result


class TestGetUserLinkedObjects:
    """Tests for get_user_linked_objects function."""

    @pytest.mark.asyncio
    async def test_get_user_linked_objects_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving linked objects for a user."""
        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import get_user_linked_objects

            result = await get_user_linked_objects(
                ctx=mock_context, user_id="00u1abc123def456", relationship_name="manager"
            )
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)

    @pytest.mark.asyncio
    async def test_get_user_linked_objects_invalid_user_id(self, mock_context):
        """Test error handling with invalid user_id."""
        from okta_mcp_server.tools.linked_objects.linked_objects import get_user_linked_objects

        result = await get_user_linked_objects(ctx=mock_context, user_id="invalid", relationship_name="manager")
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_user_linked_objects_empty_relationship(self, mock_context):
        """Test error handling with empty relationship_name."""
        from okta_mcp_server.tools.linked_objects.linked_objects import get_user_linked_objects

        result = await get_user_linked_objects(
            ctx=mock_context, user_id="00u1abc123def456", relationship_name=""
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_user_linked_objects_api_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.get_linked_objects_for_user = AsyncMock(return_value=(None, None, "API error"))

        with patch(
            "okta_mcp_server.tools.linked_objects.linked_objects.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.linked_objects.linked_objects import get_user_linked_objects

            result = await get_user_linked_objects(
                ctx=mock_context, user_id="00u1abc123def456", relationship_name="manager"
            )
            assert result.get("success") is False
            assert "error" in result
