# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import Any, Dict, List, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# CRUD Operations
# ============================================================================


@mcp.tool()
async def list_inline_hooks(ctx: Context, hook_type: Optional[str] = None) -> dict:
    """List all inline hooks in the Okta organization.

    Parameters:
        hook_type (str, optional): Filter inline hooks by type (e.g., "com.okta.oauth2.tokens.transform")

    Returns:
        Dict containing:
        - items: List of all inline hooks in the Okta organization
        - total_fetched: Number of inline hooks returned
    """
    logger.info("Listing inline hooks from Okta organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        query_params = {}
        if hook_type is not None:
            query_params["type"] = hook_type

        logger.debug(f"Calling Okta API to list inline hooks with params: {query_params}")
        hooks, _, err = await client.list_inline_hooks(query_params)

        if err:
            logger.error(f"Okta API error while listing inline hooks: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(hooks) if hooks else 0} inline hooks")
        return success_response({"items": hooks if hooks else [], "total_fetched": len(hooks) if hooks else 0})
    except Exception as e:
        logger.error(f"Exception while listing inline hooks: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_inline_hook(ctx: Context, inline_hook_id: str) -> dict:
    """Get an inline hook by ID from the Okta organization.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to retrieve

    Returns:
        Dict with success status and inline hook details.
    """
    logger.info(f"Getting inline hook with ID: {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        hook, _, err = await client.get_inline_hook(inline_hook_id)

        if err:
            logger.error(f"Okta API error while getting inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved inline hook: {inline_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while getting inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_inline_hook(
    ctx: Context, name: str, hook_type: str, url: str, headers: Optional[List[Dict[str, str]]] = None
) -> dict:
    """Create a new inline hook in the Okta organization.

    Parameters:
        name (str, required): Name for the inline hook.
        hook_type (str, required): Type of inline hook (e.g., "com.okta.oauth2.tokens.transform").
        url (str, required): URL for the inline hook endpoint.
        headers (list, optional): List of custom headers. Format: [{"key": "X-Custom", "value": "val"}]

    Returns:
        Dict with success status and created inline hook details.
    """
    logger.info("Creating new inline hook in Okta organization")
    logger.debug(f"Inline hook name: {name}, type: {hook_type}, url: {url}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {
            "name": name,
            "type": hook_type,
            "version": "1.0.0",
            "channel": {
                "type": "HTTP",
                "version": "1.0.0",
                "config": {
                    "uri": url,
                    "headers": headers or [],
                },
            },
        }

        logger.debug("Calling Okta API to create inline hook")
        hook, _, err = await client.create_inline_hook(body)

        if err:
            logger.error(f"Okta API error while creating inline hook: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created inline hook")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while creating inline hook: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_inline_hook(
    ctx: Context,
    inline_hook_id: str,
    name: Optional[str] = None,
    url: Optional[str] = None,
    headers: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Update an inline hook by ID in the Okta organization.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to update
        name (str, optional): The new name of the inline hook
        url (str, optional): The new URL for the inline hook endpoint
        headers (list, optional): The new list of custom headers

    Returns:
        Dict with success status and updated inline hook details.
    """
    logger.info(f"Updating inline hook with ID: {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if url is not None or headers is not None:
            body["channel"] = {
                "type": "HTTP",
                "version": "1.0.0",
                "config": {
                    "uri": url or "",
                    "headers": headers or [],
                },
            }

        logger.debug(f"Calling Okta API to update inline hook {inline_hook_id}")
        hook, _, err = await client.update_inline_hook(inline_hook_id, body)

        if err:
            logger.error(f"Okta API error while updating inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated inline hook: {inline_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while updating inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_inline_hook(ctx: Context, inline_hook_id: str) -> dict:
    """Delete an inline hook by ID from the Okta organization.

    This tool deletes an inline hook by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_inline_hook afterward.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for inline hook {inline_hook_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of inline hook {inline_hook_id}, please type 'DELETE'"),
            "inline_hook_id": inline_hook_id,
        }
    )


@mcp.tool()
async def confirm_delete_inline_hook(ctx: Context, inline_hook_id: str, confirmation: str) -> dict:
    """Confirm and execute inline hook deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_inline_hook.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for inline hook {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Inline hook deletion cancelled for {inline_hook_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete inline hook {inline_hook_id}")

        _, err = await client.delete_inline_hook(inline_hook_id)

        if err:
            logger.error(f"Okta API error while deleting inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted inline hook: {inline_hook_id}")
        return success_response({"message": f"Inline hook {inline_hook_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_inline_hook(ctx: Context, inline_hook_id: str) -> dict:
    """Activate an inline hook in the Okta organization.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating inline hook: {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate inline hook {inline_hook_id}")

        hook, _, err = await client.activate_inline_hook(inline_hook_id)

        if err:
            logger.error(f"Okta API error while activating inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated inline hook: {inline_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while activating inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_inline_hook(ctx: Context, inline_hook_id: str) -> dict:
    """Deactivate an inline hook in the Okta organization.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating inline hook: {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate inline hook {inline_hook_id}")

        hook, _, err = await client.deactivate_inline_hook(inline_hook_id)

        if err:
            logger.error(f"Okta API error while deactivating inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated inline hook: {inline_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while deactivating inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Execution
# ============================================================================


@mcp.tool()
async def execute_inline_hook(ctx: Context, inline_hook_id: str, payload: dict) -> dict:
    """Execute an inline hook with a payload in the Okta organization.

    Parameters:
        inline_hook_id (str, required): The ID of the inline hook to execute
        payload (dict, required): The payload to send to the inline hook endpoint

    Returns:
        Dict with success status and result of the execution operation.
    """
    logger.info(f"Executing inline hook: {inline_hook_id}")

    valid, err_msg = validate_okta_id(inline_hook_id, "inline_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to execute inline hook {inline_hook_id}")

        result, _, err = await client.execute_inline_hook(inline_hook_id, payload)

        if err:
            logger.error(f"Okta API error while executing inline hook {inline_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully executed inline hook: {inline_hook_id}")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception while executing inline hook {inline_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
