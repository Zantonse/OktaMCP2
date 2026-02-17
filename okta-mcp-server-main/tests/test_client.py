# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for the Okta client factory."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetOktaClient:
    """Tests for get_okta_client."""

    @pytest.mark.asyncio
    async def test_raises_on_none_token(self, monkeypatch):
        """get_okta_client should raise RuntimeError when keyring returns None."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=True)

            # keyring returns None — token was cleared or never stored
            with patch("okta_mcp_server.utils.client.keyring.get_password", return_value=None):
                from okta_mcp_server.utils.client import get_okta_client

                with pytest.raises(RuntimeError, match="No API token available"):
                    await get_okta_client(manager)

    @pytest.mark.asyncio
    async def test_returns_client_with_valid_token(self, monkeypatch):
        """get_okta_client should return OktaClient when token is available."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=True)

            with patch("okta_mcp_server.utils.client.keyring.get_password", return_value="valid_token"):
                from okta_mcp_server.utils.client import get_okta_client

                client = await get_okta_client(manager)
                assert client is not None

    @pytest.mark.asyncio
    async def test_reauthenticates_on_expired_token(self, monkeypatch):
        """get_okta_client should re-authenticate when token is expired."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=False)
            manager.authenticate = AsyncMock()

            # First call returns None (expired), second call returns new token
            with patch(
                "okta_mcp_server.utils.client.keyring.get_password",
                side_effect=[None, "new_token"],
            ):
                from okta_mcp_server.utils.client import get_okta_client

                client = await get_okta_client(manager)
                assert client is not None
                manager.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_after_reauth_still_no_token(self, monkeypatch):
        """get_okta_client should raise if token still None after re-authentication."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=False)
            manager.authenticate = AsyncMock()

            # Both calls return None
            with patch(
                "okta_mcp_server.utils.client.keyring.get_password",
                return_value=None,
            ):
                from okta_mcp_server.utils.client import get_okta_client

                with pytest.raises(RuntimeError, match="No API token available"):
                    await get_okta_client(manager)
