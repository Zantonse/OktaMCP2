# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for group rules management tools."""

import pytest


@pytest.mark.asyncio
async def test_list_group_rules_success(mock_context, mock_get_okta_client):
    """Test successful listing of group rules."""
    from okta_mcp_server.tools.group_rules.group_rules import list_group_rules

    result = await list_group_rules(mock_context)

    assert result["success"] is True
    assert len(result["data"]) >= 0


@pytest.mark.asyncio
async def test_list_group_rules_with_limit(mock_context, mock_get_okta_client):
    """Test listing group rules with limit parameter."""
    from okta_mcp_server.tools.group_rules.group_rules import list_group_rules

    result = await list_group_rules(mock_context, limit=10)

    assert result["success"] is True


@pytest.mark.asyncio
async def test_list_group_rules_with_after_cursor(mock_context, mock_get_okta_client):
    """Test listing group rules with pagination cursor."""
    from okta_mcp_server.tools.group_rules.group_rules import list_group_rules

    result = await list_group_rules(mock_context, after="cursor123")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_get_group_rule_success(mock_context, mock_get_okta_client):
    """Test successful retrieval of a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import get_group_rule

    result = await get_group_rule(mock_context, "0pr1abc123")

    assert result["success"] is True
    assert result["data"].id == "0pr1abc123"


@pytest.mark.asyncio
async def test_get_group_rule_invalid_id(mock_context):
    """Test get group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import get_group_rule

    result = await get_group_rule(mock_context, "")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_create_group_rule_success(mock_context, mock_get_okta_client):
    """Test successful creation of a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import create_group_rule

    result = await create_group_rule(
        mock_context,
        name="Test Rule",
        expression="user.department==\"Engineering\"",
        group_ids=["00g1abc123"]
    )

    assert result["success"] is True
    assert result["data"].name == "Test Group Rule"


@pytest.mark.asyncio
async def test_update_group_rule_success_name_only(mock_context, mock_get_okta_client):
    """Test successful update of group rule name."""
    from okta_mcp_server.tools.group_rules.group_rules import update_group_rule

    result = await update_group_rule(mock_context, "0pr1abc123", name="Updated Rule Name")

    assert result["success"] is True
    assert result["data"].id == "0pr1abc123"


@pytest.mark.asyncio
async def test_update_group_rule_success_expression_only(mock_context, mock_get_okta_client):
    """Test successful update of group rule expression."""
    from okta_mcp_server.tools.group_rules.group_rules import update_group_rule

    result = await update_group_rule(
        mock_context,
        "0pr1abc123",
        expression="user.department==\"Sales\""
    )

    assert result["success"] is True
    assert result["data"].id == "0pr1abc123"


@pytest.mark.asyncio
async def test_update_group_rule_success_group_ids_only(mock_context, mock_get_okta_client):
    """Test successful update of group rule group IDs."""
    from okta_mcp_server.tools.group_rules.group_rules import update_group_rule

    result = await update_group_rule(
        mock_context,
        "0pr1abc123",
        group_ids=["00g2xyz789", "00g3xyz456"]
    )

    assert result["success"] is True
    assert result["data"].id == "0pr1abc123"


@pytest.mark.asyncio
async def test_update_group_rule_success_all_fields(mock_context, mock_get_okta_client):
    """Test successful update of all group rule fields."""
    from okta_mcp_server.tools.group_rules.group_rules import update_group_rule

    result = await update_group_rule(
        mock_context,
        "0pr1abc123",
        name="Updated Rule",
        expression="user.department==\"Marketing\"",
        group_ids=["00g4xyz123"]
    )

    assert result["success"] is True
    assert result["data"].id == "0pr1abc123"


@pytest.mark.asyncio
async def test_update_group_rule_invalid_id(mock_context):
    """Test update group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import update_group_rule

    result = await update_group_rule(mock_context, "", name="Updated")

    assert result["success"] is False
    assert "error" in result


def test_delete_group_rule_success(mock_context):
    """Test successful deletion request for a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import delete_group_rule

    result = delete_group_rule(mock_context, "0pr1abc123")

    assert result["success"] is True
    assert result["data"]["confirmation_required"] is True
    assert "0pr1abc123" in result["data"]["message"]


def test_delete_group_rule_invalid_id(mock_context):
    """Test delete group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import delete_group_rule

    result = delete_group_rule(mock_context, "")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_confirm_delete_group_rule_success(mock_context, mock_get_okta_client):
    """Test successful confirmation and deletion of a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import confirm_delete_group_rule

    result = await confirm_delete_group_rule(mock_context, "0pr1abc123", "DELETE")

    assert result["success"] is True
    assert "deleted successfully" in result["data"]["message"]


@pytest.mark.asyncio
async def test_confirm_delete_group_rule_wrong_confirmation(mock_context):
    """Test confirm delete with wrong confirmation code."""
    from okta_mcp_server.tools.group_rules.group_rules import confirm_delete_group_rule

    result = await confirm_delete_group_rule(mock_context, "0pr1abc123", "wrong_code")

    assert result["success"] is False
    assert "Deletion cancelled" in result["error"]


@pytest.mark.asyncio
async def test_confirm_delete_group_rule_invalid_id(mock_context):
    """Test confirm delete group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import confirm_delete_group_rule

    result = await confirm_delete_group_rule(mock_context, "", "DELETE")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_activate_group_rule_success(mock_context, mock_get_okta_client):
    """Test successful activation of a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import activate_group_rule

    result = await activate_group_rule(mock_context, "0pr1abc123")

    assert result["success"] is True
    assert "activated successfully" in result["data"]["message"]


@pytest.mark.asyncio
async def test_activate_group_rule_invalid_id(mock_context):
    """Test activate group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import activate_group_rule

    result = await activate_group_rule(mock_context, "")

    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_deactivate_group_rule_success(mock_context, mock_get_okta_client):
    """Test successful deactivation of a group rule."""
    from okta_mcp_server.tools.group_rules.group_rules import deactivate_group_rule

    result = await deactivate_group_rule(mock_context, "0pr1abc123")

    assert result["success"] is True
    assert "deactivated successfully" in result["data"]["message"]


@pytest.mark.asyncio
async def test_deactivate_group_rule_invalid_id(mock_context):
    """Test deactivate group rule with invalid ID format."""
    from okta_mcp_server.tools.group_rules.group_rules import deactivate_group_rule

    result = await deactivate_group_rule(mock_context, "")

    assert result["success"] is False
    assert "error" in result
