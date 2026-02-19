# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Device Management Operations
# ============================================================================


@mcp.tool()
async def list_devices(ctx: Context) -> dict:
    """List all devices in the Okta organization.

    Returns:
        Dict containing success status and list of devices.
    """
    logger.info("Listing devices from Okta organization")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        devices, _, err = await client.list_devices()
        if err:
            logger.error(f"Okta API error while listing devices: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(devices) if devices else 0} devices")
        return success_response(devices if devices else [])
    except Exception as e:
        logger.error(f"Exception while listing devices: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_device(ctx: Context, device_id: str) -> dict:
    """Get a specific device by ID from the Okta organization.

    Parameters:
        device_id (str, required): The ID of the device to retrieve

    Returns:
        Dict with success status and device details.
    """
    logger.info(f"Getting device with ID: {device_id}")

    valid, err_msg = validate_okta_id(device_id, "device_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        device, _, err = await client.get_device(device_id)

        if err:
            logger.error(f"Okta API error while getting device {device_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved device: {device_id}")
        return success_response(device)
    except Exception as e:
        logger.error(f"Exception while getting device {device_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_device(ctx: Context, device_id: str) -> dict:
    """Request deletion of a device (confirmation required).

    IMPORTANT: This is a two-step process. This tool returns a confirmation prompt.
    You must use confirm_delete_device with the confirmation code to actually delete.

    Parameters:
        device_id (str, required): The ID of the device to delete

    Returns:
        Dict with confirmation_required flag and instructions.
    """
    logger.warning(f"Deletion requested for device {device_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(device_id, "device_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (
                f"To confirm deletion of device {device_id}, "
                "please use confirm_delete_device with confirmation='DELETE'"
            ),
            "device_id": device_id,
        }
    )


@mcp.tool()
async def confirm_delete_device(ctx: Context, device_id: str, confirmation: str) -> dict:
    """Confirm and execute device deletion.

    IMPORTANT: This completes the two-step deletion process initiated by delete_device.
    The confirmation parameter must be exactly 'DELETE' to proceed.

    Parameters:
        device_id (str, required): The ID of the device to delete
        confirmation (str, required): Confirmation code. Must be exactly 'DELETE'

    Returns:
        Dict with success status and deletion confirmation.
    """
    logger.info(f"Processing deletion confirmation for device {device_id}")

    valid, err_msg = validate_okta_id(device_id, "device_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Device deletion cancelled for {device_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_device(device_id)

        if err:
            logger.error(f"Okta API error while deleting device {device_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted device {device_id}")
        return success_response({"message": f"Device {device_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting device {device_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def list_user_devices(ctx: Context, user_id: str) -> dict:
    """List all devices for a specific user in the Okta organization.

    Parameters:
        user_id (str, required): The ID of the user

    Returns:
        Dict containing success status and list of user's devices.
    """
    logger.info(f"Listing devices for user: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        devices, _, err = await client.list_user_devices(user_id)

        if err:
            logger.error(f"Okta API error while listing devices for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(devices) if devices else 0} devices for user {user_id}")
        return success_response(devices if devices else [])
    except Exception as e:
        logger.error(f"Exception while listing devices for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
