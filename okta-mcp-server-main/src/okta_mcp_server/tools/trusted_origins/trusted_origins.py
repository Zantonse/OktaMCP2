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
from okta_mcp_server.utils.pagination import (
    build_query_params,
    create_paginated_response,
    paginate_all_results,
)
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_limit, validate_okta_id

# ============================================================================
# CRUD Operations
# ============================================================================


@mcp.tool()
async def list_trusted_origins(
    ctx: Context,
    q: Optional[str] = None,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all trusted origins in the Okta organization.

    Parameters:
        q (str, optional): Search query for trusted origin name
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)

    Returns:
        Dict containing:
        - items: List of trusted origins from the Okta organization
        - total_fetched: Number of trusted origins returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing trusted origins from Okta organization")
    logger.debug(f"Query parameters: q='{q}', limit={limit}, fetch_all={fetch_all}")

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(q=q, after=after, limit=limit)

        logger.debug("Calling Okta API to list trusted origins")
        origins, response, err = await client.list_trusted_origins(query_params)

        if err:
            logger.error(f"Okta API error while listing trusted origins: {err}")
            return error_response(sanitize_error(err))

        if not origins:
            logger.info("No trusted origins found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(origins)} trusted origins")
            all_origins, pagination_info = await paginate_all_results(response, origins)

            logger.info(
                f"Successfully retrieved {len(all_origins)} trusted origins across "
                f"{pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_origins, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(origins)} trusted origins")
            return create_paginated_response(origins, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing trusted origins: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_trusted_origin(ctx: Context, origin_id: str) -> dict:
    """Get a trusted origin by ID from the Okta organization.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to retrieve

    Returns:
        Dict with success status and trusted origin details.
    """
    logger.info(f"Getting trusted origin with ID: {origin_id}")

    valid, err_msg = validate_okta_id(origin_id, "origin_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        origin, _, err = await client.get_trusted_origin(origin_id)

        if err:
            logger.error(f"Okta API error while getting trusted origin {origin_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved trusted origin: {origin_id}")
        return success_response(origin)
    except Exception as e:
        logger.error(f"Exception while getting trusted origin {origin_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_trusted_origin(
    ctx: Context,
    name: str,
    origin: str,
    scopes: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Create a new trusted origin in the Okta organization.

    Parameters:
        name (str, required): Name for the trusted origin.
        origin (str, required): The origin URL (e.g., "https://example.com").
        scopes (list, optional): List of scopes. Format: [{"type": "CORS"}, {"type": "REDIRECT"}]
                                Default: Both CORS and REDIRECT scopes

    Returns:
        Dict with success status and created trusted origin details.
    """
    logger.info("Creating new trusted origin in Okta organization")
    logger.debug(f"Trusted origin name: {name}, origin URL: {origin}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {"name": name, "origin": origin}
        if scopes:
            body["scopes"] = scopes
        else:
            body["scopes"] = [{"type": "CORS"}, {"type": "REDIRECT"}]

        logger.debug("Calling Okta API to create trusted origin")
        origin_obj, _, err = await client.create_trusted_origin(body)

        if err:
            logger.error(f"Okta API error while creating trusted origin: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created trusted origin")
        return success_response(origin_obj)
    except Exception as e:
        logger.error(f"Exception while creating trusted origin: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_trusted_origin(
    ctx: Context,
    origin_id: str,
    name: Optional[str] = None,
    scopes: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Update a trusted origin by ID in the Okta organization.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to update
        name (str, optional): The new name of the trusted origin
        scopes (list, optional): List of scopes. Format: [{"type": "CORS"}, {"type": "REDIRECT"}]

    Returns:
        Dict with success status and updated trusted origin details.
    """
    logger.info(f"Updating trusted origin with ID: {origin_id}")

    valid, err_msg = validate_okta_id(origin_id, "origin_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if scopes is not None:
            body["scopes"] = scopes

        logger.debug(f"Calling Okta API to update trusted origin {origin_id}")
        origin_obj, _, err = await client.update_trusted_origin(origin_id, body)

        if err:
            logger.error(f"Okta API error while updating trusted origin {origin_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated trusted origin: {origin_id}")
        return success_response(origin_obj)
    except Exception as e:
        logger.error(f"Exception while updating trusted origin {origin_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_trusted_origin(ctx: Context, origin_id: str) -> dict:
    """Delete a trusted origin by ID from the Okta organization.

    This tool deletes a trusted origin by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_trusted_origin afterward.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for trusted origin {origin_id}, awaiting confirmation")

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of trusted origin {origin_id}, please type 'DELETE'"),
            "origin_id": origin_id,
        }
    )


@mcp.tool()
async def confirm_delete_trusted_origin(ctx: Context, origin_id: str, confirmation: str) -> dict:
    """Confirm and execute trusted origin deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_trusted_origin.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for trusted origin {origin_id}")

    if confirmation != "DELETE":
        logger.warning(f"Trusted origin deletion cancelled for {origin_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete trusted origin {origin_id}")

        _, err = await client.delete_trusted_origin(origin_id)

        if err:
            logger.error(f"Okta API error while deleting trusted origin {origin_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted trusted origin: {origin_id}")
        return success_response({"message": f"Trusted origin {origin_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting trusted origin {origin_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_trusted_origin(ctx: Context, origin_id: str) -> dict:
    """Activate a trusted origin in the Okta organization.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating trusted origin: {origin_id}")

    valid, err_msg = validate_okta_id(origin_id, "origin_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate trusted origin {origin_id}")

        _, err = await client.activate_trusted_origin(origin_id)

        if err:
            logger.error(f"Okta API error while activating trusted origin {origin_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated trusted origin: {origin_id}")
        return success_response({"message": f"Trusted origin {origin_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating trusted origin {origin_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_trusted_origin(ctx: Context, origin_id: str) -> dict:
    """Deactivate a trusted origin in the Okta organization.

    Parameters:
        origin_id (str, required): The ID of the trusted origin to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating trusted origin: {origin_id}")

    valid, err_msg = validate_okta_id(origin_id, "origin_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate trusted origin {origin_id}")

        _, err = await client.deactivate_trusted_origin(origin_id)

        if err:
            logger.error(f"Okta API error while deactivating trusted origin {origin_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated trusted origin: {origin_id}")
        return success_response({"message": f"Trusted origin {origin_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating trusted origin {origin_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
