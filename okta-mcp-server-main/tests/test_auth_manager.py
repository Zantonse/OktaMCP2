# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for OktaAuthManager authentication flow."""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestOktaAuthManagerInit:
    """Tests for OktaAuthManager initialization."""

    def test_init_with_required_env_vars(self, monkeypatch):
        """Test initialization with required environment variables."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()

        assert manager.org_url == "https://test.okta.com"
        assert manager.client_id == "test_client_id"
        assert manager.use_browserless_auth is False

    def test_init_adds_https_prefix(self, monkeypatch):
        """Test that https:// prefix is added if missing."""
        monkeypatch.setenv("OKTA_ORG_URL", "test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()

        assert manager.org_url == "https://test.okta.com"

    def test_init_with_browserless_auth(self, monkeypatch):
        """Test initialization with browserless auth configuration."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()

        assert manager.use_browserless_auth is True

    def test_init_with_custom_scopes(self, monkeypatch):
        """Test initialization with custom scopes."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_SCOPES", "okta.users.read okta.groups.read")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()

        assert "okta.users.read" in manager.scopes
        assert "okta.groups.read" in manager.scopes


class TestTokenValidation:
    """Tests for token validation."""

    @pytest.mark.asyncio
    async def test_is_valid_token_with_valid_token(self, monkeypatch):
        """Test is_valid_token returns True when token is valid."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("keyring.get_password", return_value="valid_token"):
            manager = OktaAuthManager()
            manager.token_timestamp = time.time()  # Recent token

            result = await manager.is_valid_token()

        assert result is True

    @pytest.mark.asyncio
    async def test_is_valid_token_with_expired_token(self, monkeypatch):
        """Test is_valid_token handles expired tokens."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with (
            patch("keyring.get_password", return_value="valid_token"),
            patch("keyring.set_password"),
        ):
            manager = OktaAuthManager()
            manager.token_timestamp = 0  # Very old token

            # Mock the authenticate method to avoid actual auth
            manager.authenticate = AsyncMock()
            manager.refresh_access_token = AsyncMock(return_value=False)

            await manager.is_valid_token()

            # When refresh fails (returns False), authenticate should be called
            assert manager.authenticate.called is True


class TestTokenRefresh:
    """Tests for token refresh."""

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, monkeypatch):
        """Test successful token refresh."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token",
            "refresh_token": "new_refresh_token",
        }

        with (
            patch("keyring.get_password", return_value="old_refresh_token"),
            patch("keyring.set_password"),
            patch("httpx.AsyncClient") as mock_client,
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            manager = OktaAuthManager()
            result = await manager.refresh_access_token()

        assert result is True

    @pytest.mark.asyncio
    async def test_refresh_access_token_no_refresh_token(self, monkeypatch):
        """Test token refresh fails when no refresh token available."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("keyring.get_password", return_value=None):
            manager = OktaAuthManager()
            result = await manager.refresh_access_token()

        assert result is False


class TestClearTokens:
    """Tests for clearing tokens."""

    def test_clear_tokens(self, monkeypatch):
        """Test that clear_tokens removes stored tokens."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("keyring.delete_password") as mock_delete:
            manager = OktaAuthManager()
            manager.token_timestamp = time.time()

            manager.clear_tokens()

        assert manager.token_timestamp == 0
        assert mock_delete.call_count >= 1


class TestTokenRefreshRaceCondition:
    """Tests for concurrent token refresh safety."""

    @pytest.mark.asyncio
    async def test_concurrent_is_valid_token_calls_authenticate_once(self, monkeypatch):
        """When multiple calls hit is_valid_token with an expired token, authenticate should only run once."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("keyring.get_password", return_value="valid_token"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.token_timestamp = 0  # Expired

            call_count = 0

            async def counting_authenticate():
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.1)
                manager.token_timestamp = time.time()

            manager.authenticate = counting_authenticate
            manager.refresh_access_token = AsyncMock(return_value=False)

            results = await asyncio.gather(*[manager.is_valid_token() for _ in range(5)])

            assert call_count == 1


class TestAuthManagerExceptions:
    """Tests that auth failures raise exceptions instead of sys.exit."""

    def test_init_missing_env_vars_raises(self, monkeypatch):
        monkeypatch.delenv("OKTA_ORG_URL", raising=False)
        monkeypatch.delenv("OKTA_CLIENT_ID", raising=False)
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with pytest.raises(RuntimeError, match="OKTA_ORG_URL and OKTA_CLIENT_ID must be set"):
            OktaAuthManager()

    @pytest.mark.asyncio
    async def test_device_auth_request_error_raises(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        import httpx
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )
            with pytest.raises(RuntimeError, match="Failed to initiate device authorization"):
                await manager._initiate_device_authorization()

    @pytest.mark.asyncio
    async def test_browserless_auth_failure_raises(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()
        manager._browserless_authenticate = AsyncMock(return_value=None)
        with pytest.raises(RuntimeError, match="Browserless authentication failed"):
            await manager.authenticate()

    @pytest.mark.asyncio
    async def test_device_flow_auth_failure_raises(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()
        manager._initiate_device_authorization = AsyncMock(
            return_value={
                "verification_uri_complete": "https://test.okta.com/activate",
                "device_code": "test",
                "interval": 1,
                "expires_in": 1,
                "start_time": 0,
            }
        )
        manager._poll_for_token = AsyncMock(return_value=None)
        with patch("webbrowser.open"):
            with pytest.raises(RuntimeError, match="Authentication failed"):
                await manager.authenticate()


class TestJsonDecodeHandling:
    """Tests for JSON decode error handling in auth flows."""

    @pytest.mark.asyncio
    async def test_browserless_auth_handles_html_response(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        mock_response.text = "<html>Error</html>"
        with patch("keyring.set_password"), patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            manager._get_client_assertion = MagicMock(return_value="fake_assertion")
            result = await manager._browserless_authenticate()
        assert result is None

    @pytest.mark.asyncio
    async def test_device_auth_handles_html_response(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        mock_response.text = "<html>Error</html>"
        mock_response.raise_for_status = MagicMock()
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            with pytest.raises(RuntimeError, match="Failed to initiate device authorization"):
                await manager._initiate_device_authorization()

    @pytest.mark.asyncio
    async def test_token_poll_handles_html_response(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        import time as time_module
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>", 0)
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            device_data = {
                "device_code": "test_code",
                "interval": 0.1,
                "expires_in": 0.5,
                "start_time": time_module.time(),
            }
            result = await manager._poll_for_token(device_data)
        assert result is None


class TestKeyringErrorHandling:
    @pytest.mark.asyncio
    async def test_browserless_auth_handles_keyring_error(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("keyring.set_password", side_effect=Exception("No keyring backend")),
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            manager._get_client_assertion = MagicMock(return_value="fake_assertion")
            result = await manager._browserless_authenticate()
        assert result == "test_token"

    @pytest.mark.asyncio
    async def test_refresh_handles_keyring_error(self, monkeypatch):
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new_token", "refresh_token": "new_refresh"}
        with (
            patch("keyring.get_password", return_value="old_refresh_token"),
            patch("keyring.set_password", side_effect=Exception("No keyring backend")),
            patch("httpx.AsyncClient") as mock_client,
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            result = await manager.refresh_access_token()
        assert result is True
