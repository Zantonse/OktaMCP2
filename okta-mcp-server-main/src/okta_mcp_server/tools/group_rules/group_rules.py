# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Group Rules Management Operations
# ============================================================================


@mcp.tool()
async def list_group_rules(ctx: Context, limit: Optional[int] = None, after: Optional[str] = None) -> dict:
    """List all group rules in the Okta organization.

    Parameters:
        limit (int, optional): Maximum number of group rules to return (default: 20, max: 200)
        after (str, optional): Pagination cursor to fetch next page of results

    Returns:
        Dict containing success status and list of group rules.
    """
    logger.info("Listing group rules from Okta organization")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        query_params = {}
        if limit is not None:
            query_params["limit"] = limit
        if after is not None:
            query_params["after"] = after

        client = await get_okta_client(manager)
        rules, _, err = await client.list_group_rules(query_params if query_params else None)
        if err:
            logger.error(f"Okta API error while listing group rules: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(rules) if rules else 0} group rules")
        return success_response(rules if rules else [])
    except Exception as e:
        logger.error(f"Exception while listing group rules: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_group_rule(ctx: Context, rule_id: str) -> dict:
    """Get a specific group rule by ID from the Okta organization.

    Parameters:
        rule_id (str, required): The ID of the group rule to retrieve

    Returns:
        Dict with success status and group rule details.
    """
    logger.info(f"Getting group rule with ID: {rule_id}")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        rule, _, err = await client.get_group_rule(rule_id)

        if err:
            logger.error(f"Okta API error while getting group rule {rule_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved group rule: {rule_id}")
        return success_response(rule)
    except Exception as e:
        logger.error(f"Exception while getting group rule {rule_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_group_rule(ctx: Context, name: str, expression: str, group_ids: list) -> dict:
    """Create a new group rule in the Okta organization.

    Parameters:
        name (str, required): The name of the group rule
        expression (str, required): The Okta expression to evaluate for group assignment
        group_ids (list, required): List of group IDs to assign users to when rule matches

    Returns:
        Dict with success status and created group rule details.
    """
    logger.info(f"Creating group rule with name: {name}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body = {
            "name": name,
            "type": "group_rule",
            "conditions": {"expression": {"type": "urn:okta:expression:1.0", "value": expression}},
            "actions": {"assignUserToGroups": {"groupIds": group_ids}},
        }

        client = await get_okta_client(manager)
        rule, _, err = await client.create_group_rule(body)

        if err:
            logger.error(f"Okta API error while creating group rule: {err}")
            return error_response(sanitize_error(err))

        rule_id = rule.id if hasattr(rule, "id") else "unknown"
        logger.info(f"Successfully created group rule: {rule_id}")
        return success_response(rule)
    except Exception as e:
        logger.error(f"Exception while creating group rule: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_group_rule(
    ctx: Context, rule_id: str, name: Optional[str] = None, expression: Optional[str] = None,
    group_ids: Optional[list] = None
) -> dict:
    """Update an existing group rule in the Okta organization.

    Parameters:
        rule_id (str, required): The ID of the group rule to update
        name (str, optional): Updated name of the group rule
        expression (str, optional): Updated Okta expression for group assignment
        group_ids (list, optional): Updated list of group IDs to assign users to

    Returns:
        Dict with success status and updated group rule details.
    """
    logger.info(f"Updating group rule with ID: {rule_id}")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body = {}
        if name is not None:
            body["name"] = name
        if expression is not None:
            body["conditions"] = {"expression": {"type": "urn:okta:expression:1.0", "value": expression}}
        if group_ids is not None:
            body["actions"] = {"assignUserToGroups": {"groupIds": group_ids}}

        client = await get_okta_client(manager)
        rule, _, err = await client.update_group_rule(rule_id, body)

        if err:
            logger.error(f"Okta API error while updating group rule {rule_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated group rule: {rule_id}")
        return success_response(rule)
    except Exception as e:
        logger.error(f"Exception while updating group rule {rule_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_group_rule(ctx: Context, rule_id: str) -> dict:
    """Request deletion of a group rule (confirmation required).

    IMPORTANT: This is a two-step process. This tool returns a confirmation prompt.
    You must use confirm_delete_group_rule with the confirmation code to actually delete.

    Parameters:
        rule_id (str, required): The ID of the group rule to delete

    Returns:
        Dict with confirmation_required flag and instructions.
    """
    logger.warning(f"Deletion requested for group rule {rule_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (
                f"To confirm deletion of group rule {rule_id}, "
                "please use confirm_delete_group_rule with confirmation='DELETE'"
            ),
            "rule_id": rule_id,
        }
    )


@mcp.tool()
async def confirm_delete_group_rule(ctx: Context, rule_id: str, confirmation: str) -> dict:
    """Confirm and execute group rule deletion.

    IMPORTANT: This completes the two-step deletion process initiated by delete_group_rule.
    The confirmation parameter must be exactly 'DELETE' to proceed.

    Parameters:
        rule_id (str, required): The ID of the group rule to delete
        confirmation (str, required): Confirmation code. Must be exactly 'DELETE'

    Returns:
        Dict with success status and deletion confirmation.
    """
    logger.info(f"Processing deletion confirmation for group rule {rule_id}")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Group rule deletion cancelled for {rule_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_group_rule(rule_id)

        if err:
            logger.error(f"Okta API error while deleting group rule {rule_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted group rule {rule_id}")
        return success_response({"message": f"Group rule {rule_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting group rule {rule_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def activate_group_rule(ctx: Context, rule_id: str) -> dict:
    """Activate a group rule in the Okta organization.

    Parameters:
        rule_id (str, required): The ID of the group rule to activate

    Returns:
        Dict with success status and activation confirmation.
    """
    logger.info(f"Activating group rule with ID: {rule_id}")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.activate_group_rule(rule_id)

        if err:
            logger.error(f"Okta API error while activating group rule {rule_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated group rule: {rule_id}")
        return success_response({"message": f"Group rule {rule_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating group rule {rule_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_group_rule(ctx: Context, rule_id: str) -> dict:
    """Deactivate a group rule in the Okta organization.

    Parameters:
        rule_id (str, required): The ID of the group rule to deactivate

    Returns:
        Dict with success status and deactivation confirmation.
    """
    logger.info(f"Deactivating group rule with ID: {rule_id}")

    valid, err_msg = validate_okta_id(rule_id, "rule_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.deactivate_group_rule(rule_id)

        if err:
            logger.error(f"Okta API error while deactivating group rule {rule_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated group rule: {rule_id}")
        return success_response({"message": f"Group rule {rule_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating group rule {rule_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
