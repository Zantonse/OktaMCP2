# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for device assurance policy management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListDeviceAssurancePolicies:
    """Test suite for list_device_assurance_policies tool."""

    @pytest.mark.asyncio
    async def test_list_device_assurance_policies_success(self, mock_context, mock_okta_client):
        """Test successful listing of all device assurance policies."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import list_device_assurance_policies

            result = await list_device_assurance_policies(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_device_assurance_policies_error(self, mock_context):
        """Test list_device_assurance_policies handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.list_device_assurance_policies.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import list_device_assurance_policies

            result = await list_device_assurance_policies(ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None


class TestGetDeviceAssurancePolicy:
    """Test suite for get_device_assurance_policy tool."""

    @pytest.mark.asyncio
    async def test_get_device_assurance_policy_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a device assurance policy."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import get_device_assurance_policy

            result = await get_device_assurance_policy(policy_id="dap1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "dap1abc123"

    @pytest.mark.asyncio
    async def test_get_device_assurance_policy_invalid_id(self, mock_context):
        """Test get_device_assurance_policy with invalid policy ID."""
        from okta_mcp_server.tools.device_assurance.device_assurance import get_device_assurance_policy

        result = await get_device_assurance_policy(policy_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_get_device_assurance_policy_error(self, mock_context):
        """Test get_device_assurance_policy handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.get_device_assurance_policy.return_value = (None, None, Exception("Policy not found"))

        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import get_device_assurance_policy

            result = await get_device_assurance_policy(policy_id="dap1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None


class TestCreateDeviceAssurancePolicy:
    """Test suite for create_device_assurance_policy tool."""

    @pytest.mark.asyncio
    async def test_create_device_assurance_policy_success(self, mock_context, mock_okta_client):
        """Test successful creation of a device assurance policy."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import create_device_assurance_policy

            result = await create_device_assurance_policy(ctx=mock_context, name="Test Policy", platform="MACOS")
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_device_assurance_policy_with_config(self, mock_context, mock_okta_client):
        """Test creating a device assurance policy with policy config."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import create_device_assurance_policy

            policy_config = {"os_version": {"minimum": "13.0"}}
            result = await create_device_assurance_policy(
                ctx=mock_context, name="Test Policy", platform="MACOS", policy_config=policy_config
            )
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_device_assurance_policy_invalid_platform(self, mock_context):
        """Test create_device_assurance_policy with invalid platform."""
        from okta_mcp_server.tools.device_assurance.device_assurance import create_device_assurance_policy

        result = await create_device_assurance_policy(
            ctx=mock_context, name="Test Policy", platform="INVALID_PLATFORM"
        )
        assert result.get("success") is False
        assert "Invalid platform" in result.get("error")

    @pytest.mark.asyncio
    async def test_create_device_assurance_policy_error(self, mock_context):
        """Test create_device_assurance_policy handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.create_device_assurance_policy.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import create_device_assurance_policy

            result = await create_device_assurance_policy(ctx=mock_context, name="Test Policy", platform="MACOS")
            assert result.get("success") is False
            assert result.get("error") is not None


class TestUpdateDeviceAssurancePolicy:
    """Test suite for update_device_assurance_policy tool."""

    @pytest.mark.asyncio
    async def test_update_device_assurance_policy_success(self, mock_context, mock_okta_client):
        """Test successful update of a device assurance policy."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import update_device_assurance_policy

            policy_config = {"name": "Updated Policy"}
            result = await update_device_assurance_policy(
                ctx=mock_context, policy_id="dap1abc123", policy_config=policy_config
            )
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_update_device_assurance_policy_invalid_id(self, mock_context):
        """Test update_device_assurance_policy with invalid policy ID."""
        from okta_mcp_server.tools.device_assurance.device_assurance import update_device_assurance_policy

        policy_config = {"name": "Updated Policy"}
        result = await update_device_assurance_policy(
            ctx=mock_context, policy_id="invalid@#$%", policy_config=policy_config
        )
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_update_device_assurance_policy_error(self, mock_context):
        """Test update_device_assurance_policy handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.replace_device_assurance_policy.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import update_device_assurance_policy

            policy_config = {"name": "Updated Policy"}
            result = await update_device_assurance_policy(
                ctx=mock_context, policy_id="dap1abc123", policy_config=policy_config
            )
            assert result.get("success") is False
            assert result.get("error") is not None


class TestDeleteDeviceAssurancePolicy:
    """Test suite for delete_device_assurance_policy tool."""

    def test_delete_device_assurance_policy_confirmation_required(self, mock_context):
        """Test delete_device_assurance_policy returns confirmation required message."""
        from okta_mcp_server.tools.device_assurance.device_assurance import delete_device_assurance_policy

        result = delete_device_assurance_policy(ctx=mock_context, policy_id="dap1abc123")
        assert result.get("success") is True
        assert result.get("data").get("confirmation_required") is True
        assert result.get("data").get("policy_id") == "dap1abc123"
        assert "DELETE" in result.get("data").get("message")

    def test_delete_device_assurance_policy_invalid_id(self, mock_context):
        """Test delete_device_assurance_policy with invalid policy ID."""
        from okta_mcp_server.tools.device_assurance.device_assurance import delete_device_assurance_policy

        result = delete_device_assurance_policy(ctx=mock_context, policy_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None


class TestConfirmDeleteDeviceAssurancePolicy:
    """Test suite for confirm_delete_device_assurance_policy tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_device_assurance_policy_success(self, mock_context, mock_okta_client):
        """Test successful deletion of a device assurance policy."""
        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import confirm_delete_device_assurance_policy

            result = await confirm_delete_device_assurance_policy(
                ctx=mock_context, policy_id="dap1abc123", confirmation="DELETE"
            )
            assert result.get("success") is True
            assert "deleted successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_confirm_delete_device_assurance_policy_invalid_id(self, mock_context):
        """Test confirm_delete_device_assurance_policy with invalid policy ID."""
        from okta_mcp_server.tools.device_assurance.device_assurance import confirm_delete_device_assurance_policy

        result = await confirm_delete_device_assurance_policy(
            ctx=mock_context, policy_id="invalid@#$%", confirmation="DELETE"
        )
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_confirm_delete_device_assurance_policy_wrong_confirmation(self, mock_context):
        """Test confirm_delete_device_assurance_policy with wrong confirmation."""
        from okta_mcp_server.tools.device_assurance.device_assurance import confirm_delete_device_assurance_policy

        result = await confirm_delete_device_assurance_policy(
            ctx=mock_context, policy_id="dap1abc123", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "Deletion cancelled" in result.get("error")

    @pytest.mark.asyncio
    async def test_confirm_delete_device_assurance_policy_error(self, mock_context):
        """Test confirm_delete_device_assurance_policy handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.delete_device_assurance_policy.return_value = (None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.device_assurance.device_assurance.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.device_assurance.device_assurance import confirm_delete_device_assurance_policy

            result = await confirm_delete_device_assurance_policy(
                ctx=mock_context, policy_id="dap1abc123", confirmation="DELETE"
            )
            assert result.get("success") is False
            assert result.get("error") is not None
