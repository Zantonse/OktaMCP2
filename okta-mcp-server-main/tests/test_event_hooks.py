# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for event hook management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListEventHooks:
    """Tests for list_event_hooks tool."""

    @pytest.mark.asyncio
    async def test_list_event_hooks_success(self, mock_context, mock_okta_client):
        """Test successful event hooks listing."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import list_event_hooks

            result = await list_event_hooks(ctx=mock_context)

            assert result.get("success") is True
            assert "items" in result.get("data", {})
            assert result.get("data", {}).get("total_fetched") >= 0

    @pytest.mark.asyncio
    async def test_list_event_hooks_error_handling(self, mock_context):
        """Test error handling when listing event hooks fails."""
        mock_client = AsyncMock()
        mock_client.list_event_hooks = AsyncMock(side_effect=Exception("API error"))

        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import list_event_hooks

            result = await list_event_hooks(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestGetEventHook:
    """Tests for get_event_hook tool."""

    @pytest.mark.asyncio
    async def test_get_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook retrieval."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import get_event_hook

            result = await get_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_event_hook_invalid_id(self, mock_context, mock_okta_client):
        """Test get_event_hook with invalid ID."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import get_event_hook

            result = await get_event_hook(event_hook_id="invalid@id!", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_event_hook_error_handling(self, mock_context):
        """Test error handling when event hook not found."""
        mock_client = AsyncMock()
        mock_client.get_event_hook = AsyncMock(side_effect=Exception("Event hook not found"))

        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import get_event_hook

            result = await get_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestCreateEventHook:
    """Tests for create_event_hook tool."""

    @pytest.mark.asyncio
    async def test_create_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook creation."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import create_event_hook

            result = await create_event_hook(
                ctx=mock_context,
                name="Test Hook",
                url="https://example.com/webhook",
                events=["user.lifecycle.create"],
            )

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_event_hook_with_headers(self, mock_context, mock_okta_client):
        """Test event hook creation with custom headers."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import create_event_hook

            headers = [{"key": "X-Custom-Header", "value": "custom-value"}]
            result = await create_event_hook(
                ctx=mock_context,
                name="Test Hook",
                url="https://example.com/webhook",
                events=["user.lifecycle.create"],
                headers=headers,
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_event_hook_multiple_events(self, mock_context, mock_okta_client):
        """Test event hook creation with multiple event types."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import create_event_hook

            events = ["user.lifecycle.create", "user.lifecycle.delete", "user.account.update_password"]
            result = await create_event_hook(
                ctx=mock_context,
                name="Multi Event Hook",
                url="https://example.com/webhook",
                events=events,
            )

            assert result.get("success") is True


class TestUpdateEventHook:
    """Tests for update_event_hook tool."""

    @pytest.mark.asyncio
    async def test_update_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook update."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import update_event_hook

            result = await update_event_hook(
                event_hook_id="who1abc123def456", ctx=mock_context, name="Updated Hook"
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_event_hook_with_url(self, mock_context, mock_okta_client):
        """Test event hook update with URL change."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import update_event_hook

            result = await update_event_hook(
                event_hook_id="who1abc123def456",
                ctx=mock_context,
                url="https://newexample.com/webhook",
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_update_event_hook_with_events(self, mock_context, mock_okta_client):
        """Test event hook update with events change."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import update_event_hook

            events = ["user.lifecycle.delete", "user.account.lock"]
            result = await update_event_hook(
                event_hook_id="who1abc123def456", ctx=mock_context, events=events
            )

            assert result.get("success") is True


class TestDeleteEventHook:
    """Tests for delete_event_hook tool."""

    @pytest.mark.asyncio
    async def test_delete_event_hook_confirmation_required(self, mock_context, mock_okta_client):
        """Test that delete_event_hook returns confirmation requirement."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import delete_event_hook

            result = delete_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data", {}).get("confirmation_required") is True
            assert "DELETE" in result.get("data", {}).get("message", "")


class TestConfirmDeleteEventHook:
    """Tests for confirm_delete_event_hook tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook deletion with confirmation."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import confirm_delete_event_hook

            result = await confirm_delete_event_hook(
                event_hook_id="who1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_confirm_delete_event_hook_wrong_confirmation(self, mock_context, mock_okta_client):
        """Test deletion with wrong confirmation."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import confirm_delete_event_hook

            result = await confirm_delete_event_hook(
                event_hook_id="who1abc123def456", confirmation="WRONG", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_event_hook_error_handling(self, mock_context):
        """Test error handling during deletion."""
        mock_client = AsyncMock()
        mock_client.delete_event_hook = AsyncMock(side_effect=Exception("Deletion failed"))

        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import confirm_delete_event_hook

            result = await confirm_delete_event_hook(
                event_hook_id="who1abc123def456", confirmation="DELETE", ctx=mock_context
            )

            assert result.get("success") is False
            assert "error" in result


class TestActivateEventHook:
    """Tests for activate_event_hook tool."""

    @pytest.mark.asyncio
    async def test_activate_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook activation."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import activate_event_hook

            result = await activate_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None


class TestDeactivateEventHook:
    """Tests for deactivate_event_hook tool."""

    @pytest.mark.asyncio
    async def test_deactivate_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook deactivation."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import deactivate_event_hook

            result = await deactivate_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None


class TestVerifyEventHook:
    """Tests for verify_event_hook tool."""

    @pytest.mark.asyncio
    async def test_verify_event_hook_success(self, mock_context, mock_okta_client):
        """Test successful event hook verification."""
        with patch(
            "okta_mcp_server.tools.event_hooks.event_hooks.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.event_hooks.event_hooks import verify_event_hook

            result = await verify_event_hook(event_hook_id="who1abc123def456", ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None
