# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.  # noqa: E501
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  # noqa: E501
# See the License for the specific language governing permissions and limitations under the License.

"""User type management tools for Okta."""

from typing import Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id


@mcp.tool()
async def list_user_types(ctx: Context) -> dict:
    """List all user types in the Okta organization.

    Returns:
        dict with success/error status and list of user types
    """
    logger.info("Listing user types from Okta organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to list user types")

        user_types, _, err = await client.list_user_types()

        if err:
            logger.error(f"Okta API error while listing user types: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(user_types) if user_types else 0} user types")
        return success_response(user_types if user_types else [])
    except Exception as e:
        logger.error(f"Exception while listing user types: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_user_type(ctx: Context, type_id: str) -> dict:
    """Get a user type by ID from the Okta organization.

    Parameters:
        type_id: The ID of the user type to retrieve

    Returns:
        dict with success/error status and user type details
    """
    logger.info(f"Getting user type with ID: {type_id}")

    valid, err_msg = validate_okta_id(type_id, "type_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get user type {type_id}")

        user_type, _, err = await client.get_user_type(type_id)

        if err:
            logger.error(f"Okta API error while getting user type {type_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved user type: {type_id}")
        return success_response(user_type)
    except Exception as e:
        logger.error(f"Exception while getting user type {type_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_user_type(ctx: Context, name: str, display_name: str, description: str) -> dict:
    """Create a new user type in the Okta organization.

    Parameters:
        name: The name of the user type
        display_name: The display name of the user type
        description: The description of the user type

    Returns:
        dict with success/error status and created user type details
    """
    logger.info(f"Creating new user type: {name}")
    logger.debug(f"Display name: {display_name}, Description: {description}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        body = {
            "name": name,
            "displayName": display_name,
            "description": description,
        }
        logger.debug("Calling Okta API to create user type")

        user_type, _, err = await client.create_user_type(body)

        if err:
            logger.error(f"Okta API error while creating user type: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created user type: {user_type.id if hasattr(user_type, 'id') else 'N/A'}")
        return success_response(user_type)
    except Exception as e:
        logger.error(f"Exception while creating user type: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_user_type(
    ctx: Context,
    type_id: str,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Update an existing user type in the Okta organization.

    Parameters:
        type_id: The ID of the user type to update
        name: The new name of the user type (optional)
        display_name: The new display name of the user type (optional)
        description: The new description of the user type (optional)

    Returns:
        dict with success/error status and updated user type details
    """
    logger.info(f"Updating user type with ID: {type_id}")

    valid, err_msg = validate_okta_id(type_id, "type_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        # Build body from non-None parameters
        body = {}
        if name is not None:
            body["name"] = name
        if display_name is not None:
            body["displayName"] = display_name
        if description is not None:
            body["description"] = description

        if not body:
            logger.warning(f"No updates provided for user type {type_id}")
            return error_response("At least one field (name, display_name, or description) must be provided")

        logger.debug(f"Calling Okta API to update user type {type_id}")

        user_type, _, err = await client.update_user_type(type_id, body)

        if err:
            logger.error(f"Okta API error while updating user type {type_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated user type: {type_id}")
        return success_response(user_type)
    except Exception as e:
        logger.error(f"Exception while updating user type {type_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_user_type(ctx: Context, type_id: str) -> dict:
    """Request deletion of a user type from the Okta organization.

    This is the first step in a two-step deletion process. Call confirm_delete_user_type
    to complete the deletion.

    Parameters:
        type_id: The ID of the user type to delete

    Returns:
        dict with confirmation request
    """
    logger.warning(f"Deletion requested for user type {type_id}")

    valid, err_msg = validate_okta_id(type_id, "type_id")
    if not valid:
        return error_response(err_msg)

    confirmation_msg = (
        f"Are you sure you want to delete user type '{type_id}'? This action cannot be undone. "
        "To confirm, call confirm_delete_user_type with confirmation='DELETE'"
    )
    return success_response(
        {
            "confirmation_required": True,
            "message": confirmation_msg,
            "type_id": type_id,
        }
    )


@mcp.tool()
async def confirm_delete_user_type(ctx: Context, type_id: str, confirmation: str) -> dict:
    """Confirm and execute deletion of a user type from the Okta organization.

    Parameters:
        type_id: The ID of the user type to delete
        confirmation: The confirmation string. Must be exactly 'DELETE' to proceed

    Returns:
        dict with success/error status and deletion confirmation
    """
    logger.info(f"Processing deletion confirmation for user type {type_id}")

    valid, err_msg = validate_okta_id(type_id, "type_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Deletion cancelled for user type {type_id}. Invalid confirmation string provided.")
        return error_response("Deletion cancelled. To confirm, provide confirmation='DELETE'")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete user type {type_id}")

        _, err = await client.delete_user_type(type_id)

        if err:
            logger.error(f"Okta API error while deleting user type {type_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted user type: {type_id}")
        return success_response({"message": f"User type '{type_id}' deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting user type {type_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
