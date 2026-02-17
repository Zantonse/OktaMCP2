# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for network zone management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListNetworkZones:
    """Tests for list_network_zones tool."""

    @pytest.mark.asyncio
    async def test_list_network_zones_success(self, mock_context, mock_okta_client):
        """Test successful network zones listing."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import list_network_zones

            result = await list_network_zones(ctx=mock_context)

            assert "items" in result
            assert result.get("fetch_all_used") is False

    @pytest.mark.asyncio
    async def test_list_network_zones_with_query(self, mock_context, mock_okta_client):
        """Test network zones listing with search query."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import list_network_zones

            result = await list_network_zones(ctx=mock_context, q="test")

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_network_zones_with_limit(self, mock_context, mock_okta_client):
        """Test network zones listing with limit parameter."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import list_network_zones

            result = await list_network_zones(ctx=mock_context, limit=50)

            assert "items" in result

    @pytest.mark.asyncio
    async def test_list_network_zones_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import list_network_zones

            # Test with limit below minimum
            result = await list_network_zones(ctx=mock_context, limit=5)
            assert "items" in result


class TestGetNetworkZone:
    """Tests for get_network_zone tool."""

    @pytest.mark.asyncio
    async def test_get_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone retrieval."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import get_network_zone

            result = await get_network_zone(zone_id="nzn1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_network_zone_error_handling(self, mock_context):
        """Test error handling when network zone not found."""
        mock_client = AsyncMock()
        mock_client.get_network_zone = AsyncMock(side_effect=Exception("Network zone not found"))

        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import get_network_zone

            result = await get_network_zone(zone_id="invalid_id", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateNetworkZone:
    """Tests for create_network_zone tool."""

    @pytest.mark.asyncio
    async def test_create_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone creation."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import create_network_zone

            result = await create_network_zone(ctx=mock_context, name="Test Zone", zone_type="IP")

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_network_zone_with_gateways(self, mock_context, mock_okta_client):
        """Test network zone creation with gateways."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import create_network_zone

            gateways = [{"type": "CIDR", "value": "10.0.0.0/8"}]
            result = await create_network_zone(ctx=mock_context, name="Test Zone", zone_type="IP", gateways=gateways)

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_network_zone_with_proxies(self, mock_context, mock_okta_client):
        """Test network zone creation with proxies."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import create_network_zone

            proxies = [{"type": "CIDR", "value": "192.168.0.0/16"}]
            result = await create_network_zone(ctx=mock_context, name="Test Zone", zone_type="IP", proxies=proxies)

            assert result.get("success") is True


class TestUpdateNetworkZone:
    """Tests for update_network_zone tool."""

    @pytest.mark.asyncio
    async def test_update_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone update."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import update_network_zone

            result = await update_network_zone(zone_id="nzn1abc123def456", ctx=mock_context, name="Updated Zone")

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_network_zone_with_gateways(self, mock_context, mock_okta_client):
        """Test network zone update with gateways."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import update_network_zone

            gateways = [{"type": "CIDR", "value": "172.16.0.0/12"}]
            result = await update_network_zone(
                zone_id="nzn1abc123def456", ctx=mock_context, name="Updated Zone", gateways=gateways
            )

            assert result.get("success") is True


class TestDeleteNetworkZone:
    """Tests for delete_network_zone tool."""

    @pytest.mark.asyncio
    async def test_delete_network_zone_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_network_zone returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import delete_network_zone

            result = delete_network_zone(zone_id="nzn1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True


class TestConfirmDeleteNetworkZone:
    """Tests for confirm_delete_network_zone tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import confirm_delete_network_zone

            result = await confirm_delete_network_zone(
                zone_id="nzn1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_network_zone_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import confirm_delete_network_zone

            result = await confirm_delete_network_zone(
                zone_id="nzn1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateNetworkZone:
    """Tests for activate_network_zone tool."""

    @pytest.mark.asyncio
    async def test_activate_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone activation."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import activate_network_zone

            result = await activate_network_zone(zone_id="nzn1abc123def456", ctx=mock_context)

            assert result.get("success") is True


class TestDeactivateNetworkZone:
    """Tests for deactivate_network_zone tool."""

    @pytest.mark.asyncio
    async def test_deactivate_network_zone_success(self, mock_context, mock_okta_client):
        """Test successful network zone deactivation."""
        with patch(
            "okta_mcp_server.tools.network_zones.network_zones.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.network_zones.network_zones import deactivate_network_zone

            result = await deactivate_network_zone(zone_id="nzn1abc123def456", ctx=mock_context)

            assert result.get("success") is True
