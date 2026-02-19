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
# Device Assurance Policy Management Operations
# ============================================================================


@mcp.tool()
async def list_device_assurance_policies(ctx: Context) -> dict:
    """List all device assurance policies in the Okta organization.

    Returns:
        Dict containing success status and list of device assurance policies.
    """
    logger.info("Listing device assurance policies from Okta organization")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        policies, _, err = await client.list_device_assurance_policies()
        if err:
            logger.error(f"Okta API error while listing device assurance policies: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(policies) if policies else 0} device assurance policies")
        return success_response(policies if policies else [])
    except Exception as e:
        logger.error(f"Exception while listing device assurance policies: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_device_assurance_policy(ctx: Context, policy_id: str) -> dict:
    """Get a specific device assurance policy by ID from the Okta organization.

    Parameters:
        policy_id (str, required): The ID of the device assurance policy to retrieve

    Returns:
        Dict with success status and device assurance policy details.
    """
    logger.info(f"Getting device assurance policy with ID: {policy_id}")

    valid, err_msg = validate_okta_id(policy_id, "policy_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        policy, _, err = await client.get_device_assurance_policy(policy_id)

        if err:
            logger.error(f"Okta API error while getting device assurance policy {policy_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved device assurance policy: {policy_id}")
        return success_response(policy)
    except Exception as e:
        logger.error(f"Exception while getting device assurance policy {policy_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_device_assurance_policy(
    ctx: Context, name: str, platform: str, policy_config: Optional[dict] = None
) -> dict:
    """Create a new device assurance policy in the Okta organization.

    Parameters:
        name (str, required): The name of the device assurance policy
        platform (str, required): The platform for the policy (MACOS, WINDOWS, ANDROID, IOS, CHROMEOS)
        policy_config (dict, optional): Additional policy configuration parameters

    Returns:
        Dict with success status and created device assurance policy details.
    """
    logger.info(f"Creating device assurance policy with name: {name}, platform: {platform}")

    valid_platforms = ["MACOS", "WINDOWS", "ANDROID", "IOS", "CHROMEOS"]
    if platform not in valid_platforms:
        error_msg = f"Invalid platform '{platform}'. Must be one of: {', '.join(valid_platforms)}"
        logger.error(error_msg)
        return error_response(error_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body = {"name": name, "platform": platform}
        if policy_config:
            body.update(policy_config)

        client = await get_okta_client(manager)
        policy, _, err = await client.create_device_assurance_policy(body)

        if err:
            logger.error(f"Okta API error while creating device assurance policy: {err}")
            return error_response(sanitize_error(err))

        policy_id = policy.id if hasattr(policy, "id") else "unknown"
        logger.info(f"Successfully created device assurance policy: {policy_id}")
        return success_response(policy)
    except Exception as e:
        logger.error(f"Exception while creating device assurance policy: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_device_assurance_policy(ctx: Context, policy_id: str, policy_config: dict) -> dict:
    """Update an existing device assurance policy in the Okta organization.

    Parameters:
        policy_id (str, required): The ID of the device assurance policy to update
        policy_config (dict, required): The updated policy configuration

    Returns:
        Dict with success status and updated device assurance policy details.
    """
    logger.info(f"Updating device assurance policy with ID: {policy_id}")

    valid, err_msg = validate_okta_id(policy_id, "policy_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        policy, _, err = await client.replace_device_assurance_policy(policy_id, policy_config)

        if err:
            logger.error(f"Okta API error while updating device assurance policy {policy_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated device assurance policy: {policy_id}")
        return success_response(policy)
    except Exception as e:
        logger.error(f"Exception while updating device assurance policy {policy_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_device_assurance_policy(ctx: Context, policy_id: str) -> dict:
    """Request deletion of a device assurance policy (confirmation required).

    IMPORTANT: This is a two-step process. This tool returns a confirmation prompt.
    You must use confirm_delete_device_assurance_policy with the confirmation code to actually delete.

    Parameters:
        policy_id (str, required): The ID of the device assurance policy to delete

    Returns:
        Dict with confirmation_required flag and instructions.
    """
    logger.warning(f"Deletion requested for device assurance policy {policy_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(policy_id, "policy_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (
                f"To confirm deletion of device assurance policy {policy_id}, "
                "please use confirm_delete_device_assurance_policy with confirmation='DELETE'"
            ),
            "policy_id": policy_id,
        }
    )


@mcp.tool()
async def confirm_delete_device_assurance_policy(ctx: Context, policy_id: str, confirmation: str) -> dict:
    """Confirm and execute device assurance policy deletion.

    IMPORTANT: This completes the two-step deletion process initiated by delete_device_assurance_policy.
    The confirmation parameter must be exactly 'DELETE' to proceed.

    Parameters:
        policy_id (str, required): The ID of the device assurance policy to delete
        confirmation (str, required): Confirmation code. Must be exactly 'DELETE'

    Returns:
        Dict with success status and deletion confirmation.
    """
    logger.info(f"Processing deletion confirmation for device assurance policy {policy_id}")

    valid, err_msg = validate_okta_id(policy_id, "policy_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Device assurance policy deletion cancelled for {policy_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_device_assurance_policy(policy_id)

        if err:
            logger.error(f"Okta API error while deleting device assurance policy {policy_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted device assurance policy {policy_id}")
        return success_response({"message": f"Device assurance policy {policy_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting device assurance policy {policy_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
