# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for behavior detection rule management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListBehaviorRules:
    """Test suite for list_behavior_rules tool."""

    @pytest.mark.asyncio
    async def test_list_behavior_rules_success(self, mock_context, mock_okta_client):
        """Test successful listing of all behavior detection rules."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import list_behavior_rules

            result = await list_behavior_rules(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_behavior_rules_error(self, mock_context):
        """Test list_behavior_rules handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.list_behavior_detection_rules.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import list_behavior_rules

            result = await list_behavior_rules(ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_list_behavior_rules_empty(self, mock_context):
        """Test list_behavior_rules with no rules."""
        mock_client = AsyncMock()
        mock_client.list_behavior_detection_rules.return_value = ([], None, None)

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import list_behavior_rules

            result = await list_behavior_rules(ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") == []


class TestGetBehaviorRule:
    """Test suite for get_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_get_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of a behavior rule."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import get_behavior_rule

            result = await get_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").id == "bhv1abc123"

    @pytest.mark.asyncio
    async def test_get_behavior_rule_invalid_id(self, mock_context):
        """Test get_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import get_behavior_rule

        result = await get_behavior_rule(behavior_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_get_behavior_rule_error(self, mock_context):
        """Test get_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.get_behavior_detection_rule.return_value = (None, None, Exception("Rule not found"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import get_behavior_rule

            result = await get_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None


class TestCreateBehaviorRule:
    """Test suite for create_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_create_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful creation of a behavior rule."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import create_behavior_rule

            result = await create_behavior_rule(
                ctx=mock_context, name="Test Rule", behavior_type="ANOMALY_VELOCITY"
            )
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_behavior_rule_with_settings(self, mock_context, mock_okta_client):
        """Test creating a behavior rule with settings."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import create_behavior_rule

            settings = {"maxEventsUsedForEvaluation": 100}
            result = await create_behavior_rule(
                ctx=mock_context, name="Test Rule", behavior_type="ANOMALY_LOCATION", settings=settings
            )
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_behavior_rule_invalid_type(self, mock_context):
        """Test create_behavior_rule with invalid behavior type."""
        from okta_mcp_server.tools.behaviors.behaviors import create_behavior_rule

        result = await create_behavior_rule(ctx=mock_context, name="Test Rule", behavior_type="INVALID_TYPE")
        assert result.get("success") is False
        assert "Invalid behavior_type" in result.get("error")

    @pytest.mark.asyncio
    async def test_create_behavior_rule_error(self, mock_context):
        """Test create_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.create_behavior_detection_rule.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import create_behavior_rule

            result = await create_behavior_rule(
                ctx=mock_context, name="Test Rule", behavior_type="ANOMALY_DEVICE"
            )
            assert result.get("success") is False
            assert result.get("error") is not None


class TestUpdateBehaviorRule:
    """Test suite for update_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_update_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful update of a behavior rule."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import update_behavior_rule

            result = await update_behavior_rule(ctx=mock_context, behavior_id="bhv1abc123", name="Updated Rule")
            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_update_behavior_rule_invalid_id(self, mock_context):
        """Test update_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import update_behavior_rule

        result = await update_behavior_rule(ctx=mock_context, behavior_id="invalid@#$%", name="Updated Rule")
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_update_behavior_rule_invalid_type(self, mock_context):
        """Test update_behavior_rule with invalid behavior type."""
        from okta_mcp_server.tools.behaviors.behaviors import update_behavior_rule

        result = await update_behavior_rule(
            ctx=mock_context, behavior_id="bhv1abc123", behavior_type="INVALID_TYPE"
        )
        assert result.get("success") is False
        assert "Invalid behavior_type" in result.get("error")

    @pytest.mark.asyncio
    async def test_update_behavior_rule_error(self, mock_context):
        """Test update_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.update_behavior_detection_rule.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import update_behavior_rule

            result = await update_behavior_rule(ctx=mock_context, behavior_id="bhv1abc123", name="Updated")
            assert result.get("success") is False
            assert result.get("error") is not None


class TestDeleteBehaviorRule:
    """Test suite for delete_behavior_rule tool."""

    def test_delete_behavior_rule_confirmation_required(self, mock_context):
        """Test delete_behavior_rule returns confirmation required message."""
        from okta_mcp_server.tools.behaviors.behaviors import delete_behavior_rule

        result = delete_behavior_rule(ctx=mock_context, behavior_id="bhv1abc123")
        assert result.get("success") is True
        assert result.get("data").get("confirmation_required") is True
        assert result.get("data").get("behavior_id") == "bhv1abc123"
        assert "DELETE" in result.get("data").get("message")

    def test_delete_behavior_rule_invalid_id(self, mock_context):
        """Test delete_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import delete_behavior_rule

        result = delete_behavior_rule(ctx=mock_context, behavior_id="invalid@#$%")
        assert result.get("success") is False
        assert result.get("error") is not None

    def test_delete_behavior_rule_sync_not_async(self):
        """Test delete_behavior_rule is synchronous (not async)."""
        import inspect

        from okta_mcp_server.tools.behaviors.behaviors import delete_behavior_rule

        # delete_behavior_rule should be a regular function, not a coroutine
        assert not inspect.iscoroutinefunction(delete_behavior_rule)


class TestConfirmDeleteBehaviorRule:
    """Test suite for confirm_delete_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_confirm_delete_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful behavior rule deletion with correct confirmation."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import confirm_delete_behavior_rule

            result = await confirm_delete_behavior_rule(
                ctx=mock_context, behavior_id="bhv1abc123", confirmation="DELETE"
            )
            assert result.get("success") is True
            assert "deleted successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_confirm_delete_behavior_rule_wrong_confirmation(self, mock_context):
        """Test deletion fails with incorrect confirmation."""
        from okta_mcp_server.tools.behaviors.behaviors import confirm_delete_behavior_rule

        result = await confirm_delete_behavior_rule(
            ctx=mock_context, behavior_id="bhv1abc123", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "must be exactly 'DELETE'" in result.get("error")

    @pytest.mark.asyncio
    async def test_confirm_delete_behavior_rule_invalid_id(self, mock_context):
        """Test confirm_delete_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import confirm_delete_behavior_rule

        result = await confirm_delete_behavior_rule(
            ctx=mock_context, behavior_id="invalid@#$%", confirmation="DELETE"
        )
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_confirm_delete_behavior_rule_error(self, mock_context):
        """Test confirm_delete_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.delete_behavior_detection_rule.return_value = (None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import confirm_delete_behavior_rule

            result = await confirm_delete_behavior_rule(
                ctx=mock_context, behavior_id="bhv1abc123", confirmation="DELETE"
            )
            assert result.get("success") is False
            assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_confirm_delete_behavior_rule_is_async(self):
        """Test confirm_delete_behavior_rule is asynchronous."""
        import inspect

        from okta_mcp_server.tools.behaviors.behaviors import confirm_delete_behavior_rule

        # confirm_delete_behavior_rule should be a coroutine function
        assert inspect.iscoroutinefunction(confirm_delete_behavior_rule)


class TestActivateBehaviorRule:
    """Test suite for activate_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_activate_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful activation of a behavior rule."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import activate_behavior_rule

            result = await activate_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "activated successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_activate_behavior_rule_invalid_id(self, mock_context):
        """Test activate_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import activate_behavior_rule

        result = await activate_behavior_rule(behavior_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_activate_behavior_rule_error(self, mock_context):
        """Test activate_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.activate_behavior_detection_rule.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import activate_behavior_rule

            result = await activate_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None


class TestDeactivateBehaviorRule:
    """Test suite for deactivate_behavior_rule tool."""

    @pytest.mark.asyncio
    async def test_deactivate_behavior_rule_success(self, mock_context, mock_okta_client):
        """Test successful deactivation of a behavior rule."""
        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import deactivate_behavior_rule

            result = await deactivate_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is True
            assert "deactivated successfully" in result.get("data").get("message")

    @pytest.mark.asyncio
    async def test_deactivate_behavior_rule_invalid_id(self, mock_context):
        """Test deactivate_behavior_rule with invalid behavior ID."""
        from okta_mcp_server.tools.behaviors.behaviors import deactivate_behavior_rule

        result = await deactivate_behavior_rule(behavior_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_deactivate_behavior_rule_error(self, mock_context):
        """Test deactivate_behavior_rule handles Okta API errors."""
        mock_client = AsyncMock()
        mock_client.deactivate_behavior_detection_rule.return_value = (None, None, Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.behaviors.behaviors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.behaviors.behaviors import deactivate_behavior_rule

            result = await deactivate_behavior_rule(behavior_id="bhv1abc123", ctx=mock_context)
            assert result.get("success") is False
            assert result.get("error") is not None
