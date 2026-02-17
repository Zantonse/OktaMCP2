# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for the Okta schemas management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetUserSchema:
    """Tests for get_user_schema function."""

    @pytest.mark.asyncio
    async def test_get_user_schema_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving the default user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_user_schema

            result = await get_user_schema(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "user"

    @pytest.mark.asyncio
    async def test_get_user_schema_error(self, mock_context):
        """Test error handling when retrieving user schema fails."""
        mock_client = AsyncMock()
        mock_client.get_user_schema = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_user_schema

            result = await get_user_schema(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetUserSchemaByType:
    """Tests for get_user_schema_by_type function."""

    @pytest.mark.asyncio
    async def test_get_user_schema_by_type_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving user schema for a specific type."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_user_schema_by_type

            result = await get_user_schema_by_type(type_id="oty1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "user"

    @pytest.mark.asyncio
    async def test_get_user_schema_by_type_error(self, mock_context):
        """Test error handling when retrieving user schema by type fails."""
        mock_client = AsyncMock()
        mock_client.get_user_schema = AsyncMock(return_value=(None, None, "User type not found"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_user_schema_by_type

            result = await get_user_schema_by_type(type_id="invalid", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestListUserTypes:
    """Tests for list_user_types function."""

    @pytest.mark.asyncio
    async def test_list_user_types_success(self, mock_context, mock_okta_client):
        """Test successfully listing user types."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import list_user_types

            result = await list_user_types(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0
            assert result.get("data")[0].name == "Default"

    @pytest.mark.asyncio
    async def test_list_user_types_error(self, mock_context):
        """Test error handling when listing user types fails."""
        mock_client = AsyncMock()
        mock_client.list_user_types = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import list_user_types

            result = await list_user_types(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestAddUserSchemaProperty:
    """Tests for add_user_schema_property function."""

    @pytest.mark.asyncio
    async def test_add_user_schema_property_success(self, mock_context, mock_okta_client):
        """Test successfully adding a custom property to user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import add_user_schema_property

            result = await add_user_schema_property(
                property_name="customAttribute",
                ctx=mock_context,
                type_id="default",
                property_config={"title": "Custom Attribute", "type": "string"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "user"

    @pytest.mark.asyncio
    async def test_add_user_schema_property_with_defaults(self, mock_context, mock_okta_client):
        """Test adding a property with default configuration."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import add_user_schema_property

            result = await add_user_schema_property(
                property_name="simpleAttribute",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_add_user_schema_property_with_constraints(self, mock_context, mock_okta_client):
        """Test adding a property with validation constraints."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import add_user_schema_property

            result = await add_user_schema_property(
                property_name="constrainedAttribute",
                ctx=mock_context,
                property_config={
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "pattern": "^[a-zA-Z0-9]*$",
                },
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_add_user_schema_property_error(self, mock_context):
        """Test error handling when adding a property fails."""
        mock_client = AsyncMock()
        mock_client.update_user_profile = AsyncMock(return_value=(None, None, "Invalid property"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import add_user_schema_property

            result = await add_user_schema_property(
                property_name="invalidAttribute",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result


class TestUpdateUserSchemaProperty:
    """Tests for update_user_schema_property function."""

    @pytest.mark.asyncio
    async def test_update_user_schema_property_success(self, mock_context, mock_okta_client):
        """Test successfully updating a custom property in user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_user_schema_property

            result = await update_user_schema_property(
                property_name="customAttribute",
                ctx=mock_context,
                type_id="default",
                property_config={"title": "Updated Attribute", "description": "Updated description"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "user"

    @pytest.mark.asyncio
    async def test_update_user_schema_property_with_enum(self, mock_context, mock_okta_client):
        """Test updating a property with enum values."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_user_schema_property

            result = await update_user_schema_property(
                property_name="statusAttribute",
                ctx=mock_context,
                property_config={
                    "type": "string",
                    "enum": ["active", "inactive", "pending"],
                },
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_user_schema_property_error(self, mock_context):
        """Test error handling when updating a property fails."""
        mock_client = AsyncMock()
        mock_client.update_user_profile = AsyncMock(return_value=(None, None, "Property not found"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_user_schema_property

            result = await update_user_schema_property(
                property_name="nonexistent",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result


class TestRemoveUserSchemaProperty:
    """Tests for remove_user_schema_property function."""

    @pytest.mark.asyncio
    async def test_remove_user_schema_property_success(self, mock_context, mock_okta_client):
        """Test successfully removing a custom property from user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import remove_user_schema_property

            result = await remove_user_schema_property(
                property_name="customAttribute",
                ctx=mock_context,
                type_id="default",
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "user"

    @pytest.mark.asyncio
    async def test_remove_user_schema_property_error(self, mock_context):
        """Test error handling when removing a property fails."""
        mock_client = AsyncMock()
        mock_client.update_user_profile = AsyncMock(return_value=(None, None, "Cannot remove property"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import remove_user_schema_property

            result = await remove_user_schema_property(
                property_name="customAttribute",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result


class TestGetAppUserSchema:
    """Tests for get_app_user_schema function."""

    @pytest.mark.asyncio
    async def test_get_app_user_schema_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving app-specific user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_app_user_schema

            result = await get_app_user_schema(app_id="0oa123", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "app_user"

    @pytest.mark.asyncio
    async def test_get_app_user_schema_error(self, mock_context):
        """Test error handling when retrieving app user schema fails."""
        mock_client = AsyncMock()
        mock_client.get_application_user_schema = AsyncMock(return_value=(None, None, "Application not found"))

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import get_app_user_schema

            result = await get_app_user_schema(app_id="invalid", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdateAppUserSchema:
    """Tests for update_app_user_schema function."""

    @pytest.mark.asyncio
    async def test_update_app_user_schema_success(self, mock_context, mock_okta_client):
        """Test successfully updating app-specific user schema."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_app_user_schema

            result = await update_app_user_schema(
                app_id="0oa123",
                ctx=mock_context,
                schema_config={
                    "definitions": {"custom": {"properties": {"appField": {"type": "string"}}}},
                },
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "app_user"

    @pytest.mark.asyncio
    async def test_update_app_user_schema_with_defaults(self, mock_context, mock_okta_client):
        """Test updating app user schema with default configuration."""
        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_app_user_schema

            result = await update_app_user_schema(
                app_id="0oa123",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_app_user_schema_error(self, mock_context):
        """Test error handling when updating app user schema fails."""
        mock_client = AsyncMock()
        mock_client.update_application_user_profile = AsyncMock(
            return_value=(None, None, "Invalid schema configuration")
        )

        with patch(
            "okta_mcp_server.tools.schemas.schemas.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.schemas.schemas import update_app_user_schema

            result = await update_app_user_schema(
                app_id="0oa123",
                ctx=mock_context,
                schema_config={"invalid": "config"},
            )
            assert result.get("success") is False
            assert "error" in result
