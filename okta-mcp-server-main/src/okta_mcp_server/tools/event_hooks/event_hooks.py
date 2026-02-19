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
async def list_event_hooks(ctx: Context) -> dict:
    """List all event hooks in the Okta organization.

    Returns:
        Dict containing:
        - items: List of all event hooks in the Okta organization
        - total_fetched: Number of event hooks returned
    """
    logger.info("Listing event hooks from Okta organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug("Calling Okta API to list event hooks")
        hooks, _, err = await client.list_event_hooks()

        if err:
            logger.error(f"Okta API error while listing event hooks: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(hooks) if hooks else 0} event hooks")
        return success_response({"items": hooks if hooks else [], "total_fetched": len(hooks) if hooks else 0})
    except Exception as e:
        logger.error(f"Exception while listing event hooks: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_event_hook(ctx: Context, event_hook_id: str) -> dict:
    """Get an event hook by ID from the Okta organization.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to retrieve

    Returns:
        Dict with success status and event hook details.
    """
    logger.info(f"Getting event hook with ID: {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        hook, _, err = await client.get_event_hook(event_hook_id)

        if err:
            logger.error(f"Okta API error while getting event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved event hook: {event_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while getting event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_event_hook(
    ctx: Context, name: str, url: str, events: List[str], headers: Optional[List[Dict[str, str]]] = None
) -> dict:
    """Create a new event hook in the Okta organization.

    Parameters:
        name (str, required): Name for the event hook.
        url (str, required): URL for the event hook endpoint.
        events (list, required): List of event types to trigger the hook (e.g., ["user.lifecycle.create"]).
        headers (list, optional): List of custom headers. Format: [{"key": "X-Custom", "value": "val"}]

    Returns:
        Dict with success status and created event hook details.
    """
    logger.info("Creating new event hook in Okta organization")
    logger.debug(f"Event hook name: {name}, url: {url}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {
            "name": name,
            "events": {"type": "EVENT_TYPE", "items": events},
            "channel": {
                "type": "HTTP",
                "version": "1.0.0",
                "config": {"uri": url, "headers": headers or []},
            },
        }

        logger.debug("Calling Okta API to create event hook")
        hook, _, err = await client.create_event_hook(body)

        if err:
            logger.error(f"Okta API error while creating event hook: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created event hook")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while creating event hook: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_event_hook(
    ctx: Context,
    event_hook_id: str,
    name: Optional[str] = None,
    url: Optional[str] = None,
    events: Optional[List[str]] = None,
    headers: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Update an event hook by ID in the Okta organization.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to update
        name (str, optional): The new name of the event hook
        url (str, optional): The new URL for the event hook endpoint
        events (list, optional): The new list of event types
        headers (list, optional): The new list of custom headers

    Returns:
        Dict with success status and updated event hook details.
    """
    logger.info(f"Updating event hook with ID: {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if events is not None:
            body["events"] = {"type": "EVENT_TYPE", "items": events}
        if url is not None or headers is not None:
            body["channel"] = {
                "type": "HTTP",
                "version": "1.0.0",
                "config": {
                    "uri": url or "",
                    "headers": headers or [],
                },
            }

        logger.debug(f"Calling Okta API to update event hook {event_hook_id}")
        hook, _, err = await client.update_event_hook(event_hook_id, body)

        if err:
            logger.error(f"Okta API error while updating event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated event hook: {event_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while updating event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_event_hook(ctx: Context, event_hook_id: str) -> dict:
    """Delete an event hook by ID from the Okta organization.

    This tool deletes an event hook by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_event_hook afterward.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for event hook {event_hook_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of event hook {event_hook_id}, please type 'DELETE'"),
            "event_hook_id": event_hook_id,
        }
    )


@mcp.tool()
async def confirm_delete_event_hook(ctx: Context, event_hook_id: str, confirmation: str) -> dict:
    """Confirm and execute event hook deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_event_hook.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for event hook {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Event hook deletion cancelled for {event_hook_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete event hook {event_hook_id}")

        _, err = await client.delete_event_hook(event_hook_id)

        if err:
            logger.error(f"Okta API error while deleting event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted event hook: {event_hook_id}")
        return success_response({"message": f"Event hook {event_hook_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_event_hook(ctx: Context, event_hook_id: str) -> dict:
    """Activate an event hook in the Okta organization.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating event hook: {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate event hook {event_hook_id}")

        hook, _, err = await client.activate_event_hook(event_hook_id)

        if err:
            logger.error(f"Okta API error while activating event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated event hook: {event_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while activating event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_event_hook(ctx: Context, event_hook_id: str) -> dict:
    """Deactivate an event hook in the Okta organization.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating event hook: {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate event hook {event_hook_id}")

        hook, _, err = await client.deactivate_event_hook(event_hook_id)

        if err:
            logger.error(f"Okta API error while deactivating event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated event hook: {event_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while deactivating event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def verify_event_hook(ctx: Context, event_hook_id: str) -> dict:
    """Verify an event hook endpoint in the Okta organization.

    Parameters:
        event_hook_id (str, required): The ID of the event hook to verify

    Returns:
        Dict with success status and result of the verification operation.
    """
    logger.info(f"Verifying event hook: {event_hook_id}")

    valid, err_msg = validate_okta_id(event_hook_id, "event_hook_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to verify event hook {event_hook_id}")

        hook, _, err = await client.verify_event_hook(event_hook_id)

        if err:
            logger.error(f"Okta API error while verifying event hook {event_hook_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully verified event hook: {event_hook_id}")
        return success_response(hook)
    except Exception as e:
        logger.error(f"Exception while verifying event hook {event_hook_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
