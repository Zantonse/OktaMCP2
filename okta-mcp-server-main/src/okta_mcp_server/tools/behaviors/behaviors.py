# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import Any, Dict, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Behavior Detection Rules CRUD Operations
# ============================================================================


@mcp.tool()
async def list_behavior_rules(ctx: Context) -> dict:
    """List all behavior detection rules configured in the Okta organization.

    Returns:
        Dict with list of behavior detection rules including their types, names, and statuses.
    """
    logger.info("Listing behavior detection rules from Okta organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to list behavior detection rules")

        rules, _, err = await client.list_behavior_detection_rules()

        if err:
            logger.error(f"Okta API error while listing behavior detection rules: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(rules) if rules else 0} behavior detection rules")
        return success_response(rules if rules else [])
    except Exception as e:
        logger.error(f"Exception while listing behavior detection rules: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_behavior_rule(behavior_id: str, ctx: Context) -> dict:
    """Get behavior detection rule details and settings.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to retrieve.

    Returns:
        Dict with behavior rule details and settings.
    """
    logger.info(f"Getting behavior detection rule with ID: {behavior_id}")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get behavior detection rule {behavior_id}")

        rule, _, err = await client.get_behavior_detection_rule(behavior_id)

        if err:
            logger.error(f"Okta API error while getting behavior detection rule {behavior_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved behavior detection rule: {behavior_id}")
        return success_response(rule)
    except Exception as e:
        logger.error(
            f"Exception while getting behavior detection rule {behavior_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_behavior_rule(
    ctx: Context, name: str, behavior_type: str, settings: Optional[Dict[str, Any]] = None
) -> dict:
    """Create a new behavior detection rule.

    Parameters:
        name (str, required): The name of the behavior rule.
        behavior_type (str, required): The type of behavior rule. Must be one of:
            - ANOMALY_VELOCITY: Detects anomalous patterns in authentication velocity
            - ANOMALY_LOCATION: Detects logins from new or unusual locations
            - ANOMALY_DEVICE: Detects logins from new devices
        settings (dict, optional): Additional settings for the rule (e.g., thresholds, exclusions).

    Returns:
        Dict with created behavior rule details.
    """
    logger.info(f"Creating behavior detection rule: {name}")

    valid_types = {"ANOMALY_VELOCITY", "ANOMALY_LOCATION", "ANOMALY_DEVICE"}
    if behavior_type not in valid_types:
        err_msg = f"Invalid behavior_type '{behavior_type}'. Must be one of: {', '.join(valid_types)}"
        logger.error(err_msg)
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body: Dict[str, Any] = {"name": name, "type": behavior_type}
        if settings is not None:
            body["settings"] = settings

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to create behavior detection rule: {name}")

        rule, _, err = await client.create_behavior_detection_rule(body)

        if err:
            logger.error(f"Okta API error while creating behavior detection rule: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created behavior detection rule: {rule.id if hasattr(rule, 'id') else 'unknown'}")
        return success_response(rule)
    except Exception as e:
        logger.error(f"Exception while creating behavior detection rule: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_behavior_rule(
    ctx: Context,
    behavior_id: str,
    name: Optional[str] = None,
    behavior_type: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
) -> dict:
    """Update an existing behavior detection rule.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to update.
        name (str, optional): The new name for the behavior rule.
        behavior_type (str, optional): The new type for the behavior rule. Must be one of:
            - ANOMALY_VELOCITY
            - ANOMALY_LOCATION
            - ANOMALY_DEVICE
        settings (dict, optional): Updated settings for the rule.

    Returns:
        Dict with updated behavior rule details.
    """
    logger.info(f"Updating behavior detection rule: {behavior_id}")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    if behavior_type is not None:
        valid_types = {"ANOMALY_VELOCITY", "ANOMALY_LOCATION", "ANOMALY_DEVICE"}
        if behavior_type not in valid_types:
            err_msg = f"Invalid behavior_type '{behavior_type}'. Must be one of: {', '.join(valid_types)}"
            logger.error(err_msg)
            return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if behavior_type is not None:
            body["type"] = behavior_type
        if settings is not None:
            body["settings"] = settings

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to update behavior detection rule {behavior_id}")

        rule, _, err = await client.update_behavior_detection_rule(behavior_id, body)

        if err:
            logger.error(f"Okta API error while updating behavior detection rule {behavior_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated behavior detection rule: {behavior_id}")
        return success_response(rule)
    except Exception as e:
        logger.error(f"Exception while updating behavior detection rule {behavior_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Behavior Detection Rules Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_behavior_rule(ctx: Context, behavior_id: str) -> dict:
    """Request deletion of a behavior detection rule (confirmation required).

    This is the first step of a two-step deletion process. The user must confirm
    the deletion by calling confirm_delete_behavior_rule with the confirmation token.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to delete.

    Returns:
        Dict with confirmation_required flag and message for the user to confirm deletion.
    """
    logger.warning(f"Deletion requested for behavior rule {behavior_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (
                f"To confirm deletion of behavior rule {behavior_id}, "
                "please call confirm_delete_behavior_rule with confirmation='DELETE'"
            ),
            "behavior_id": behavior_id,
        }
    )


@mcp.tool()
async def confirm_delete_behavior_rule(ctx: Context, behavior_id: str, confirmation: str) -> dict:
    """Confirm and execute deletion of a behavior detection rule.

    This is the second step of a two-step deletion process. The user must provide
    the correct confirmation string to proceed with deletion.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to delete.
        confirmation (str, required): Confirmation string. Must be exactly 'DELETE' to proceed.

    Returns:
        Dict with success status of the deletion operation.
    """
    logger.warning(f"Deletion confirmation received for behavior rule {behavior_id}")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Incorrect confirmation string provided for behavior rule {behavior_id}")
        return error_response("Deletion cancelled. Confirmation string must be exactly 'DELETE'.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete behavior detection rule {behavior_id}")

        _, err = await client.delete_behavior_detection_rule(behavior_id)

        if err:
            logger.error(f"Okta API error while deleting behavior detection rule {behavior_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted behavior detection rule: {behavior_id}")
        return success_response({"message": f"Behavior rule {behavior_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting behavior detection rule {behavior_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Behavior Detection Rules Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_behavior_rule(behavior_id: str, ctx: Context) -> dict:
    """Activate a behavior detection rule for the organization.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to activate.

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating behavior detection rule: {behavior_id}")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate behavior detection rule {behavior_id}")

        rule, _, err = await client.activate_behavior_detection_rule(behavior_id)

        if err:
            logger.error(f"Okta API error while activating behavior detection rule {behavior_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated behavior detection rule: {behavior_id}")
        return success_response(
            {
                "message": f"Behavior rule {behavior_id} activated successfully",
                "rule": rule,
            }
        )
    except Exception as e:
        logger.error(f"Exception while activating behavior detection rule {behavior_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_behavior_rule(behavior_id: str, ctx: Context) -> dict:
    """Deactivate a behavior detection rule for the organization.

    Parameters:
        behavior_id (str, required): The ID of the behavior rule to deactivate.

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating behavior detection rule: {behavior_id}")

    valid, err_msg = validate_okta_id(behavior_id, "behavior_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate behavior detection rule {behavior_id}")

        rule, _, err = await client.deactivate_behavior_detection_rule(behavior_id)

        if err:
            logger.error(f"Okta API error while deactivating behavior detection rule {behavior_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated behavior detection rule: {behavior_id}")
        return success_response(
            {
                "message": f"Behavior rule {behavior_id} deactivated successfully",
                "rule": rule,
            }
        )
    except Exception as e:
        logger.error(f"Exception while deactivating behavior detection rule {behavior_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
