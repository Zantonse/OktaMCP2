# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta authenticators management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListAuthenticators:
    """Tests for list_authenticators function."""

    @pytest.mark.asyncio
    async def test_list_authenticators_success(self, mock_context, mock_okta_client):
        """Test successfully listing all authenticators."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import list_authenticators

            result = await list_authenticators(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_authenticators_error(self, mock_context):
        """Test error handling when listing authenticators fails."""
        mock_client = AsyncMock()
        mock_client.list_authenticators = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import list_authenticators

            result = await list_authenticators(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetAuthenticator:
    """Tests for get_authenticator function."""

    @pytest.mark.asyncio
    async def test_get_authenticator_success(self, mock_context, mock_okta_client):
        """Test successfully getting authenticator details."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import get_authenticator

            result = await get_authenticator(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "aut1abc123"

    @pytest.mark.asyncio
    async def test_get_authenticator_error(self, mock_context):
        """Test error handling when getting authenticator fails."""
        mock_client = AsyncMock()
        mock_client.get_authenticator = AsyncMock(return_value=(None, None, "Authenticator not found"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import get_authenticator

            result = await get_authenticator(authenticator_id="invalid_id", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestActivateAuthenticator:
    """Tests for activate_authenticator function."""

    @pytest.mark.asyncio
    async def test_activate_authenticator_success(self, mock_context, mock_okta_client):
        """Test successfully activating an authenticator."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import activate_authenticator

            result = await activate_authenticator(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "message" in result.get("data", {})
            assert "activated" in result.get("data", {}).get("message", "").lower()

    @pytest.mark.asyncio
    async def test_activate_authenticator_error(self, mock_context):
        """Test error handling when activating authenticator fails."""
        mock_client = AsyncMock()
        mock_client.activate_authenticator = AsyncMock(return_value=(None, "Activation failed"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import activate_authenticator

            result = await activate_authenticator(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestDeactivateAuthenticator:
    """Tests for deactivate_authenticator function."""

    @pytest.mark.asyncio
    async def test_deactivate_authenticator_success(self, mock_context, mock_okta_client):
        """Test successfully deactivating an authenticator."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import deactivate_authenticator

            result = await deactivate_authenticator(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "message" in result.get("data", {})
            assert "deactivated" in result.get("data", {}).get("message", "").lower()

    @pytest.mark.asyncio
    async def test_deactivate_authenticator_error(self, mock_context):
        """Test error handling when deactivating authenticator fails."""
        mock_client = AsyncMock()
        mock_client.deactivate_authenticator = AsyncMock(return_value=(None, "Deactivation failed"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import deactivate_authenticator

            result = await deactivate_authenticator(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestListAuthenticatorMethods:
    """Tests for list_authenticator_methods function."""

    @pytest.mark.asyncio
    async def test_list_authenticator_methods_success(self, mock_context, mock_okta_client):
        """Test successfully listing authenticator methods."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import list_authenticator_methods

            result = await list_authenticator_methods(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_authenticator_methods_error(self, mock_context):
        """Test error handling when listing authenticator methods fails."""
        mock_client = AsyncMock()
        mock_client.list_authenticator_methods = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import list_authenticator_methods

            result = await list_authenticator_methods(authenticator_id="aut1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetAuthenticatorMethod:
    """Tests for get_authenticator_method function."""

    @pytest.mark.asyncio
    async def test_get_authenticator_method_success(self, mock_context, mock_okta_client):
        """Test successfully getting authenticator method details."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import get_authenticator_method

            result = await get_authenticator_method(
                authenticator_id="aut1abc123", method_type="push", ctx=mock_context
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").type == "push"

    @pytest.mark.asyncio
    async def test_get_authenticator_method_error(self, mock_context):
        """Test error handling when getting authenticator method fails."""
        mock_client = AsyncMock()
        mock_client.get_authenticator_method = AsyncMock(return_value=(None, None, "Method not found"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import get_authenticator_method

            result = await get_authenticator_method(
                authenticator_id="aut1abc123", method_type="invalid", ctx=mock_context
            )
            assert result.get("success") is False
            assert "error" in result


class TestActivateAuthenticatorMethod:
    """Tests for activate_authenticator_method function."""

    @pytest.mark.asyncio
    async def test_activate_authenticator_method_success(self, mock_context, mock_okta_client):
        """Test successfully activating an authenticator method."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import activate_authenticator_method

            result = await activate_authenticator_method(
                authenticator_id="aut1abc123", method_type="push", ctx=mock_context
            )
            assert result.get("success") is True
            assert "message" in result.get("data", {})
            assert "activated" in result.get("data", {}).get("message", "").lower()

    @pytest.mark.asyncio
    async def test_activate_authenticator_method_error(self, mock_context):
        """Test error handling when activating authenticator method fails."""
        mock_client = AsyncMock()
        mock_client.activate_authenticator_method = AsyncMock(return_value=(None, "Activation failed"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import activate_authenticator_method

            result = await activate_authenticator_method(
                authenticator_id="aut1abc123", method_type="push", ctx=mock_context
            )
            assert result.get("success") is False
            assert "error" in result


class TestDeactivateAuthenticatorMethod:
    """Tests for deactivate_authenticator_method function."""

    @pytest.mark.asyncio
    async def test_deactivate_authenticator_method_success(self, mock_context, mock_okta_client):
        """Test successfully deactivating an authenticator method."""
        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import deactivate_authenticator_method

            result = await deactivate_authenticator_method(
                authenticator_id="aut1abc123", method_type="push", ctx=mock_context
            )
            assert result.get("success") is True
            assert "message" in result.get("data", {})
            assert "deactivated" in result.get("data", {}).get("message", "").lower()

    @pytest.mark.asyncio
    async def test_deactivate_authenticator_method_error(self, mock_context):
        """Test error handling when deactivating authenticator method fails."""
        mock_client = AsyncMock()
        mock_client.deactivate_authenticator_method = AsyncMock(return_value=(None, "Deactivation failed"))

        with patch(
            "okta_mcp_server.tools.authenticators.authenticators.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.authenticators.authenticators import deactivate_authenticator_method

            result = await deactivate_authenticator_method(
                authenticator_id="aut1abc123", method_type="push", ctx=mock_context
            )
            assert result.get("success") is False
            assert "error" in result
