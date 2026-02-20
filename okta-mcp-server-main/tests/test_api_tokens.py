# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for API token management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListApiTokens:
    """Tests for list_api_tokens function."""

    @pytest.mark.asyncio
    async def test_list_api_tokens_success(self, mock_context, mock_okta_client):
        """Test successful listing of API tokens."""
        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import list_api_tokens

            result = await list_api_tokens(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert len(result.get("data", [])) > 0

    @pytest.mark.asyncio
    async def test_list_api_tokens_api_error(self, mock_context):
        """Test listing API tokens with API error."""
        mock_client = AsyncMock()
        mock_client.list_api_tokens.return_value = (None, None, "API Error")

        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import list_api_tokens

            result = await list_api_tokens(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetApiToken:
    """Tests for get_api_token function."""

    @pytest.mark.asyncio
    async def test_get_api_token_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a specific API token."""
        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import get_api_token

            result = await get_api_token(ctx=mock_context, token_id="tok1abc123")
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_get_api_token_invalid_id(self, mock_context):
        """Test get_api_token with invalid token ID."""
        from okta_mcp_server.tools.api_tokens.api_tokens import get_api_token

        result = await get_api_token(ctx=mock_context, token_id="invalid@123")
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_api_token_api_error(self, mock_context):
        """Test get_api_token with API error."""
        mock_client = AsyncMock()
        mock_client.get_api_token.return_value = (None, None, "API Error")

        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import get_api_token

            result = await get_api_token(ctx=mock_context, token_id="tok1abc123")
            assert result.get("success") is False
            assert "error" in result


class TestRevokeApiToken:
    """Tests for revoke_api_token function."""

    def test_revoke_api_token_returns_confirmation(self, mock_context):
        """Test revoke_api_token returns confirmation request."""
        from okta_mcp_server.tools.api_tokens.api_tokens import revoke_api_token

        result = revoke_api_token(ctx=mock_context, token_id="tok1abc123")
        assert result.get("success") is True
        assert result.get("data", {}).get("confirmation_required") is True
        assert "message" in result.get("data", {})
        assert result.get("data", {}).get("token_id") == "tok1abc123"

    def test_revoke_api_token_invalid_id(self, mock_context):
        """Test revoke_api_token with invalid token ID."""
        from okta_mcp_server.tools.api_tokens.api_tokens import revoke_api_token

        result = revoke_api_token(ctx=mock_context, token_id="invalid@123")
        assert result.get("success") is False
        assert "error" in result


class TestConfirmRevokeApiToken:
    """Tests for confirm_revoke_api_token function."""

    @pytest.mark.asyncio
    async def test_confirm_revoke_api_token_success(self, mock_context, mock_okta_client):
        """Test successful API token revocation."""
        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import confirm_revoke_api_token

            result = await confirm_revoke_api_token(
                ctx=mock_context, token_id="tok1abc123", confirmation="REVOKE"
            )
            assert result.get("success") is True
            assert "message" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_confirm_revoke_api_token_wrong_confirmation(self, mock_context):
        """Test confirm_revoke_api_token with wrong confirmation."""
        from okta_mcp_server.tools.api_tokens.api_tokens import confirm_revoke_api_token

        result = await confirm_revoke_api_token(
            ctx=mock_context, token_id="tok1abc123", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_revoke_api_token_invalid_id(self, mock_context):
        """Test confirm_revoke_api_token with invalid token ID."""
        from okta_mcp_server.tools.api_tokens.api_tokens import confirm_revoke_api_token

        result = await confirm_revoke_api_token(
            ctx=mock_context, token_id="invalid", confirmation="REVOKE"
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_revoke_api_token_api_error(self, mock_context):
        """Test confirm_revoke_api_token with API error."""
        mock_client = AsyncMock()
        mock_client.revoke_api_token.return_value = (None, "API Error")

        with patch(
            "okta_mcp_server.tools.api_tokens.api_tokens.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.api_tokens.api_tokens import confirm_revoke_api_token

            result = await confirm_revoke_api_token(
                ctx=mock_context, token_id="tok1abc123", confirmation="REVOKE"
            )
            assert result.get("success") is False
            assert "error" in result
