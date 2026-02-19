# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to
# in writing, software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

"""Tests for profile mapping management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListProfileMappings:
    """Test suite for list_profile_mappings tool."""

    @pytest.mark.asyncio
    async def test_list_profile_mappings_success(self, mock_context, mock_okta_client):
        """Test successful listing of all profile mappings."""
        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import list_profile_mappings

            result = await list_profile_mappings(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_profile_mappings_with_filters(self, mock_context, mock_okta_client):
        """Test listing profile mappings with query filters."""
        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import list_profile_mappings

            result = await list_profile_mappings(
                ctx=mock_context,
                source_id="0oa1abc123",
                target_id="oty1abc123",
                limit=10,
            )
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)

    @pytest.mark.asyncio
    async def test_list_profile_mappings_error(self, mock_context):
        """Test list_profile_mappings handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.list_profile_mappings.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import list_profile_mappings

            result = await list_profile_mappings(ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_list_profile_mappings_empty(self, mock_context):
        """Test list_profile_mappings with no mappings."""
        mock_client = AsyncMock()
        mock_client.list_profile_mappings.return_value = ([], None, None)

        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import list_profile_mappings

            result = await list_profile_mappings(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") == []


class TestGetProfileMapping:
    """Test suite for get_profile_mapping tool."""

    @pytest.mark.asyncio
    async def test_get_profile_mapping_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a profile mapping."""
        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import get_profile_mapping

            result = await get_profile_mapping(ctx=mock_context, mapping_id="prm1abc123def456")
            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "prm1abc123def456"

    @pytest.mark.asyncio
    async def test_get_profile_mapping_invalid_id(self, mock_context):
        """Test get_profile_mapping with invalid mapping ID."""
        from okta_mcp_server.tools.profile_mappings.profile_mappings import get_profile_mapping

        result = await get_profile_mapping(ctx=mock_context, mapping_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_get_profile_mapping_error(self, mock_context):
        """Test get_profile_mapping handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.get_profile_mapping.return_value = (None, None, Exception("Mapping not found"))

        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import get_profile_mapping

            result = await get_profile_mapping(ctx=mock_context, mapping_id="prm1abc123def456")
            assert result.get("success") is False
            assert result.get("error") is not None


class TestUpdateProfileMapping:
    """Test suite for update_profile_mapping tool."""

    @pytest.mark.asyncio
    async def test_update_profile_mapping_success(self, mock_context, mock_okta_client):
        """Test successful update of a profile mapping."""
        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import update_profile_mapping

            mapping_config = {
                "properties": {
                    "firstName": {"expression": "appuser.givenName"},
                    "lastName": {"expression": "appuser.familyName"},
                }
            }
            result = await update_profile_mapping(
                ctx=mock_context, mapping_id="prm1abc123def456", mapping_config=mapping_config
            )
            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "prm1abc123def456"

    @pytest.mark.asyncio
    async def test_update_profile_mapping_invalid_id(self, mock_context):
        """Test update_profile_mapping with invalid mapping ID."""
        from okta_mcp_server.tools.profile_mappings.profile_mappings import update_profile_mapping

        mapping_config = {"properties": {"firstName": {"expression": "appuser.firstName"}}}
        result = await update_profile_mapping(
            ctx=mock_context, mapping_id="invalid@#$%", mapping_config=mapping_config
        )
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_update_profile_mapping_error(self, mock_context):
        """Test update_profile_mapping handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.update_profile_mapping.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.profile_mappings.profile_mappings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.profile_mappings.profile_mappings import update_profile_mapping

            mapping_config = {"properties": {"firstName": {"expression": "appuser.firstName"}}}
            result = await update_profile_mapping(
                ctx=mock_context, mapping_id="prm1abc123def456", mapping_config=mapping_config
            )
            assert result.get("success") is False
            assert result.get("error") is not None
