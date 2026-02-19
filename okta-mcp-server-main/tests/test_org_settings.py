# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for organization settings tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetOrgSettings:
    """Tests for get_org_settings tool."""

    @pytest.mark.asyncio
    async def test_get_org_settings_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of organization settings."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_settings

            result = await get_org_settings(ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").company_name == "Test Org"
            assert result.get("data").website == "https://test.example.com"

    @pytest.mark.asyncio
    async def test_get_org_settings_api_error(self, mock_context):
        """Test error handling when Okta API returns error."""
        mock_client = AsyncMock()
        mock_client.get_org_settings = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_settings

            result = await get_org_settings(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestUpdateOrgSettings:
    """Tests for update_org_settings tool."""

    @pytest.mark.asyncio
    async def test_update_org_settings_success(self, mock_context, mock_okta_client):
        """Test successful update of organization settings."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import update_org_settings

            settings = {"companyName": "Updated Org"}
            result = await update_org_settings(ctx=mock_context, settings=settings)

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").company_name == "Updated Org"

    @pytest.mark.asyncio
    async def test_update_org_settings_with_multiple_fields(self, mock_context, mock_okta_client):
        """Test successful update with multiple organization settings fields."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import update_org_settings

            settings = {
                "companyName": "New Company",
                "website": "https://newsite.com",
                "phoneNumber": "+1-555-1234",
            }
            result = await update_org_settings(ctx=mock_context, settings=settings)

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").company_name == "New Company"
            assert result.get("data").website == "https://newsite.com"

    @pytest.mark.asyncio
    async def test_update_org_settings_api_error(self, mock_context):
        """Test error handling when Okta API returns error during update."""
        mock_client = AsyncMock()
        mock_client.partial_update_org_setting = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import update_org_settings

            result = await update_org_settings(ctx=mock_context, settings={"companyName": "Test"})

            assert result.get("success") is False
            assert "error" in result


class TestGetOrgContactTypes:
    """Tests for get_org_contact_types tool."""

    @pytest.mark.asyncio
    async def test_get_org_contact_types_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of organization contact types."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_types

            result = await get_org_contact_types(ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None
            assert len(result.get("data")) == 2
            assert any(ct.get("contactType") == "TECHNICAL" for ct in result.get("data"))
            assert any(ct.get("contactType") == "BILLING" for ct in result.get("data"))

    @pytest.mark.asyncio
    async def test_get_org_contact_types_api_error(self, mock_context):
        """Test error handling when Okta API returns error."""
        mock_client = AsyncMock()
        mock_client.get_org_contact_types = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_types

            result = await get_org_contact_types(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestGetOrgContactUser:
    """Tests for get_org_contact_user tool."""

    @pytest.mark.asyncio
    async def test_get_org_contact_user_technical_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of technical contact user."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_user

            result = await get_org_contact_user(ctx=mock_context, contact_type="TECHNICAL")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").contact_type == "TECHNICAL"

    @pytest.mark.asyncio
    async def test_get_org_contact_user_billing_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of billing contact user."""
        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_user

            result = await get_org_contact_user(ctx=mock_context, contact_type="BILLING")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").contact_type == "BILLING"

    @pytest.mark.asyncio
    async def test_get_org_contact_user_invalid_contact_type(self, mock_context):
        """Test error handling with invalid contact_type."""
        from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_user

        result = await get_org_contact_user(ctx=mock_context, contact_type="INVALID")

        assert result.get("success") is False
        assert "error" in result
        assert "Invalid contact_type" in result.get("error")

    @pytest.mark.asyncio
    async def test_get_org_contact_user_api_error(self, mock_context):
        """Test error handling when Okta API returns error."""
        mock_client = AsyncMock()
        mock_client.get_org_contact_user = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.org_settings.org_settings.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.org_settings.org_settings import get_org_contact_user

            result = await get_org_contact_user(ctx=mock_context, contact_type="TECHNICAL")

            assert result.get("success") is False
            assert "error" in result
