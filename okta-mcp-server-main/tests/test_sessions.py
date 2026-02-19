# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for session management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetSession:
    """Tests for get_session tool."""

    @pytest.mark.asyncio
    async def test_get_session_success(self, mock_context, mock_okta_client):
        """Test successful session retrieval."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import get_session

            result = await get_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "ses1abc123def456"

    @pytest.mark.asyncio
    async def test_get_session_invalid_id(self, mock_context):
        """Test get_session with invalid ID format."""
        from okta_mcp_server.tools.sessions.sessions import get_session

        result = await get_session(ctx=mock_context, session_id="invalid_id")

        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_session_api_error(self, mock_context):
        """Test error handling when Okta API returns error."""
        mock_client = AsyncMock()
        mock_client.get_session = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import get_session

            result = await get_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is False
            assert "error" in result


class TestCreateSession:
    """Tests for create_session tool."""

    @pytest.mark.asyncio
    async def test_create_session_success(self, mock_context, mock_okta_client):
        """Test successful session creation."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import create_session

            result = await create_session(ctx=mock_context, session_token="token123")

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_session_with_empty_token(self, mock_context, mock_okta_client):
        """Test session creation with empty token."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import create_session

            result = await create_session(ctx=mock_context, session_token="")

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_session_api_error(self, mock_context):
        """Test error handling when Okta API returns error during creation."""
        mock_client = AsyncMock()
        mock_client.create_session = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import create_session

            result = await create_session(ctx=mock_context, session_token="token123")

            assert result.get("success") is False
            assert "error" in result


class TestRefreshSession:
    """Tests for refresh_session tool."""

    @pytest.mark.asyncio
    async def test_refresh_session_success(self, mock_context, mock_okta_client):
        """Test successful session refresh."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import refresh_session

            result = await refresh_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "ses1abc123def456"

    @pytest.mark.asyncio
    async def test_refresh_session_invalid_id(self, mock_context):
        """Test refresh_session with invalid ID format."""
        from okta_mcp_server.tools.sessions.sessions import refresh_session

        result = await refresh_session(ctx=mock_context, session_id="invalid_id")

        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_refresh_session_api_error(self, mock_context):
        """Test error handling when Okta API returns error during refresh."""
        mock_client = AsyncMock()
        mock_client.refresh_session = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import refresh_session

            result = await refresh_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is False
            assert "error" in result


class TestCloseSession:
    """Tests for close_session tool."""

    @pytest.mark.asyncio
    async def test_close_session_success(self, mock_context, mock_okta_client):
        """Test successful session closure."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import close_session

            result = await close_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is True
            assert "message" in result.get("data")

    @pytest.mark.asyncio
    async def test_close_session_invalid_id(self, mock_context):
        """Test close_session with invalid ID format."""
        from okta_mcp_server.tools.sessions.sessions import close_session

        result = await close_session(ctx=mock_context, session_id="invalid_id")

        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_close_session_api_error(self, mock_context):
        """Test error handling when Okta API returns error during close."""
        mock_client = AsyncMock()
        mock_client.close_session = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import close_session

            result = await close_session(ctx=mock_context, session_id="ses1abc123def456")

            assert result.get("success") is False
            assert "error" in result


class TestRevokeUserSessions:
    """Tests for revoke_user_sessions tool."""

    @pytest.mark.asyncio
    async def test_revoke_user_sessions_success(self, mock_context, mock_okta_client):
        """Test successful user sessions revocation."""
        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import revoke_user_sessions

            result = await revoke_user_sessions(ctx=mock_context, user_id="00u1abc123def456")

            assert result.get("success") is True
            assert "message" in result.get("data")

    @pytest.mark.asyncio
    async def test_revoke_user_sessions_invalid_user_id(self, mock_context):
        """Test revoke_user_sessions with invalid user ID format."""
        from okta_mcp_server.tools.sessions.sessions import revoke_user_sessions

        result = await revoke_user_sessions(ctx=mock_context, user_id="invalid_id")

        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_revoke_user_sessions_api_error(self, mock_context):
        """Test error handling when Okta API returns error during revoke."""
        mock_client = AsyncMock()
        mock_client.revoke_user_sessions = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.sessions.sessions.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.sessions.sessions import revoke_user_sessions

            result = await revoke_user_sessions(ctx=mock_context, user_id="00u1abc123def456")

            assert result.get("success") is False
            assert "error" in result
