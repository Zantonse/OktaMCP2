# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for inline hook management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListInlineHooks:
    """Tests for list_inline_hooks tool."""

    @pytest.mark.asyncio
    async def test_list_inline_hooks_success(self, mock_context, mock_okta_client):
        """Test successful inline hooks listing."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import list_inline_hooks

            result = await list_inline_hooks(ctx=mock_context)

            assert result.get("success") is True
            assert "items" in result.get("data", {})
            assert result.get("data", {}).get("total_fetched") >= 0

    @pytest.mark.asyncio
    async def test_list_inline_hooks_with_type_filter(self, mock_context, mock_okta_client):
        """Test listing inline hooks with type filter."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import list_inline_hooks

            result = await list_inline_hooks(ctx=mock_context, hook_type="com.okta.oauth2.tokens.transform")

            assert result.get("success") is True
            assert "items" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_list_inline_hooks_error_handling(self, mock_context):
        """Test error handling when listing inline hooks fails."""
        mock_client = AsyncMock()
        mock_client.list_inline_hooks = AsyncMock(side_effect=Exception("API error"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import list_inline_hooks

            result = await list_inline_hooks(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestGetInlineHook:
    """Tests for get_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_get_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook retrieval."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import get_inline_hook

            result = await get_inline_hook(inline_hook_id="inh1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test get_inline_hook with invalid ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import get_inline_hook

            result = await get_inline_hook(inline_hook_id="invalid@id!", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_inline_hook_error_handling(self, mock_context):
        """Test error handling when inline hook not found."""
        mock_client = AsyncMock()
        mock_client.get_inline_hook = AsyncMock(side_effect=Exception("Inline hook not found"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import get_inline_hook

            result = await get_inline_hook(inline_hook_id="inh1abc123def456", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateInlineHook:
    """Tests for create_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_create_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook creation."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import create_inline_hook

            result = await create_inline_hook(
                ctx=mock_context,
                name="Test Hook",
                hook_type="com.okta.oauth2.tokens.transform",
                url="https://example.com/webhook",
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_inline_hook_with_headers(self, mock_context, mock_okta_client):
        """Test inline hook creation with custom headers."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import create_inline_hook

            headers = [{"key": "X-Custom-Header", "value": "custom-value"}]
            result = await create_inline_hook(
                ctx=mock_context,
                name="Test Hook",
                hook_type="com.okta.oauth2.tokens.transform",
                url="https://example.com/webhook",
                headers=headers,
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_inline_hook_error_handling(self, mock_context):
        """Test error handling during inline hook creation."""
        mock_client = AsyncMock()
        mock_client.create_inline_hook = AsyncMock(side_effect=Exception("Creation failed"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import create_inline_hook

            result = await create_inline_hook(
                ctx=mock_context,
                name="Test Hook",
                hook_type="com.okta.oauth2.tokens.transform",
                url="https://example.com/webhook",
            )

            assert result.get("success") is False
            assert "error" in result


class TestUpdateInlineHook:
    """Tests for update_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_update_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook update."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import update_inline_hook

            result = await update_inline_hook(
                inline_hook_id="inh1abc123def456", ctx=mock_context, name="Updated Hook"
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_inline_hook_with_url(self, mock_context, mock_okta_client):
        """Test inline hook update with URL change."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import update_inline_hook

            result = await update_inline_hook(
                inline_hook_id="inh1abc123def456",
                ctx=mock_context,
                url="https://newexample.com/webhook",
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test update with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import update_inline_hook

            result = await update_inline_hook(
                inline_hook_id="invalid@id!", ctx=mock_context, name="Updated Hook"
            )

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_update_inline_hook_error_handling(self, mock_context):
        """Test error handling during inline hook update."""
        mock_client = AsyncMock()
        mock_client.update_inline_hook = AsyncMock(side_effect=Exception("Update failed"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import update_inline_hook

            result = await update_inline_hook(
                inline_hook_id="inh1abc123def456", ctx=mock_context, name="Updated Hook"
            )

            assert result.get("success") is False
            assert "error" in result


class TestDeleteInlineHook:
    """Tests for delete_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_delete_inline_hook_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_inline_hook returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import delete_inline_hook

            result = delete_inline_hook(inline_hook_id="inh1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True
            assert "DELETE" in result.get("data", {}).get("message", "")

    def test_delete_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test delete with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import delete_inline_hook

            result = delete_inline_hook(inline_hook_id="invalid@id!", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestConfirmDeleteInlineHook:
    """Tests for confirm_delete_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import confirm_delete_inline_hook

            result = await confirm_delete_inline_hook(
                inline_hook_id="inh1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_inline_hook_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import confirm_delete_inline_hook

            result = await confirm_delete_inline_hook(
                inline_hook_id="inh1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test deletion confirmation with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import confirm_delete_inline_hook

            result = await confirm_delete_inline_hook(
                inline_hook_id="invalid@id!", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_inline_hook_error_handling(self, mock_context):
        """Test error handling during deletion."""
        mock_client = AsyncMock()
        mock_client.delete_inline_hook = AsyncMock(side_effect=Exception("Deletion failed"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import confirm_delete_inline_hook

            result = await confirm_delete_inline_hook(
                inline_hook_id="inh1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateInlineHook:
    """Tests for activate_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_activate_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook activation."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import activate_inline_hook

            result = await activate_inline_hook(inline_hook_id="inh1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_activate_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test activate with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import activate_inline_hook

            result = await activate_inline_hook(inline_hook_id="invalid@id!", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestDeactivateInlineHook:
    """Tests for deactivate_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_deactivate_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook deactivation."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import deactivate_inline_hook

            result = await deactivate_inline_hook(inline_hook_id="inh1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_deactivate_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test deactivate with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import deactivate_inline_hook

            result = await deactivate_inline_hook(inline_hook_id="invalid@id!", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestExecuteInlineHook:
    """Tests for execute_inline_hook tool."""

    @pytest.mark.asyncio
    async def test_execute_inline_hook_success(self, mock_context, mock_okta_client):
        """Test successful inline hook execution."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import execute_inline_hook

            payload = {"test": "data"}
            result = await execute_inline_hook(
                inline_hook_id="inh1abc123def456", ctx=mock_context, payload=payload
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_execute_inline_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test execute with invalid inline hook ID."""
        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import execute_inline_hook

            payload = {"test": "data"}
            result = await execute_inline_hook(
                inline_hook_id="invalid@id!", ctx=mock_context, payload=payload
            )

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_execute_inline_hook_error_handling(self, mock_context):
        """Test error handling during inline hook execution."""
        mock_client = AsyncMock()
        mock_client.execute_inline_hook = AsyncMock(side_effect=Exception("Execution failed"))

        with patch(
            "okta_mcp_server.tools.inline_hooks.inline_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.inline_hooks.inline_hooks import execute_inline_hook

            payload = {"test": "data"}
            result = await execute_inline_hook(
                inline_hook_id="inh1abc123def456", ctx=mock_context, payload=payload
            )

            assert result.get("success") is False
            assert "error" in result
