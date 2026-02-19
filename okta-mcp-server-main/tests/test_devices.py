# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to
# in writing, software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

"""Tests for device management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListDevices:
    """Test suite for list_devices tool."""

    @pytest.mark.asyncio
    async def test_list_devices_success(self, mock_context, mock_okta_client):
        """Test successful listing of all devices."""
        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_devices

            result = await list_devices(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_devices_error(self, mock_context):
        """Test list_devices handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.list_devices.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_devices

            result = await list_devices(ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_list_devices_empty(self, mock_context):
        """Test list_devices with no devices."""
        mock_client = AsyncMock()
        mock_client.list_devices.return_value = ([], None, None)

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_devices

            result = await list_devices(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") == []


class TestGetDevice:
    """Test suite for get_device tool."""

    @pytest.mark.asyncio
    async def test_get_device_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a device."""
        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.devices.devices import get_device

            result = await get_device(ctx=mock_context, device_id="guo1abc123def456")
            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "guo1abc123def456"

    @pytest.mark.asyncio
    async def test_get_device_invalid_id(self, mock_context):
        """Test get_device with invalid device ID."""
        from okta_mcp_server.tools.devices.devices import get_device

        result = await get_device(ctx=mock_context, device_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_get_device_error(self, mock_context):
        """Test get_device handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.get_device.return_value = (None, None, Exception("Device not found"))

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import get_device

            result = await get_device(ctx=mock_context, device_id="guo1abc123def456")
            assert result.get("success") is False
            assert result.get("error") is not None


class TestDeleteDevice:
    """Test suite for delete_device tool."""

    def test_delete_device_confirmation_required(self, mock_context):
        """Test delete_device returns confirmation required message."""
        from okta_mcp_server.tools.devices.devices import delete_device

        result = delete_device(ctx=mock_context, device_id="guo1abc123def456")
        assert result.get("success") is True
        assert result.get("data").get("confirmation_required") is True
        assert result.get("data").get("device_id") == "guo1abc123def456"
        assert "DELETE" in result.get("data").get("message")

    def test_delete_device_invalid_id(self, mock_context):
        """Test delete_device with invalid device ID."""
        from okta_mcp_server.tools.devices.devices import delete_device

        result = delete_device(ctx=mock_context, device_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None

    def test_delete_device_sync_not_async(self, mock_context):
        """Test delete_device is synchronous (not async)."""
        import inspect

        from okta_mcp_server.tools.devices.devices import delete_device

        # delete_device should be a regular function, not a coroutine
        assert not inspect.iscoroutinefunction(delete_device)


class TestConfirmDeleteDevice:
    """Test suite for confirm_delete_device tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_device_success(self, mock_context, mock_okta_client):
        """Test successful device deletion with correct confirmation."""
        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.devices.devices import confirm_delete_device

            result = await confirm_delete_device(
                ctx=mock_context, device_id="guo1abc123def456", confirmation="DELETE"
            )
            assert result.get("success") is True
            assert "deleted successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_confirm_delete_device_wrong_confirmation(self, mock_context):
        """Test deletion fails with incorrect confirmation."""
        from okta_mcp_server.tools.devices.devices import confirm_delete_device

        result = await confirm_delete_device(
            ctx=mock_context, device_id="guo1abc123def456", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "not provided correctly" in result.get("error")

    @pytest.mark.asyncio
    async def test_confirm_delete_device_invalid_id(self, mock_context):
        """Test confirm_delete_device with invalid device ID."""
        from okta_mcp_server.tools.devices.devices import confirm_delete_device

        result = await confirm_delete_device(
            ctx=mock_context, device_id="invalid@#$%", confirmation="DELETE"
        )
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_confirm_delete_device_error(self, mock_context):
        """Test confirm_delete_device handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.delete_device.return_value = (None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import confirm_delete_device

            result = await confirm_delete_device(
                ctx=mock_context, device_id="guo1abc123def456", confirmation="DELETE"
            )
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_confirm_delete_device_is_async(self):
        """Test confirm_delete_device is asynchronous."""
        import inspect

        from okta_mcp_server.tools.devices.devices import confirm_delete_device

        # confirm_delete_device should be a coroutine function
        assert inspect.iscoroutinefunction(confirm_delete_device)


class TestListUserDevices:
    """Test suite for list_user_devices tool."""

    @pytest.mark.asyncio
    async def test_list_user_devices_success(self, mock_context, mock_okta_client):
        """Test successful listing of user devices."""
        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_user_devices

            result = await list_user_devices(ctx=mock_context, user_id="00u1abc123def456")
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_user_devices_invalid_user_id(self, mock_context):
        """Test list_user_devices with invalid user ID."""
        from okta_mcp_server.tools.devices.devices import list_user_devices

        result = await list_user_devices(ctx=mock_context, user_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_list_user_devices_error(self, mock_context):
        """Test list_user_devices handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.list_user_devices.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_user_devices

            result = await list_user_devices(ctx=mock_context, user_id="00u1abc123def456")
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_list_user_devices_empty(self, mock_context):
        """Test list_user_devices with no devices for user."""
        mock_client = AsyncMock()
        mock_client.list_user_devices.return_value = ([], None, None)

        with patch(
            "okta_mcp_server.tools.devices.devices.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.devices.devices import list_user_devices

            result = await list_user_devices(ctx=mock_context, user_id="00u1abc123def456")
            assert result.get("success") is True
            assert result.get("data") == []
