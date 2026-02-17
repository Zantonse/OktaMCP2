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

# ============================================================================
# CRUD Operations
# ============================================================================


@mcp.tool()
async def list_network_zones(
    ctx: Context,
    q: Optional[str] = None,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all network zones in the Okta organization.

    Parameters:
        q (str, optional): Search query for network zone name
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)

    Returns:
        Dict containing:
        - items: List of network zones from the Okta organization
        - total_fetched: Number of network zones returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing network zones from Okta organization")
    logger.debug(f"Query parameters: q='{q}', limit={limit}, fetch_all={fetch_all}")

    # Validate limit parameter range
    if limit is not None:
        if limit < 20:
            logger.warning(f"Limit {limit} is below minimum (20), setting to 20")
            limit = 20
        elif limit > 100:
            logger.warning(f"Limit {limit} exceeds maximum (100), setting to 100")
            limit = 100

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(q=q, after=after, limit=limit)

        logger.debug("Calling Okta API to list network zones")
        zones, response, err = await client.list_network_zones(query_params)

        if err:
            logger.error(f"Okta API error while listing network zones: {err}")
            return error_response(str(err))

        if not zones:
            logger.info("No network zones found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(zones)} network zones")
            all_zones, pagination_info = await paginate_all_results(response, zones)

            logger.info(
                f"Successfully retrieved {len(all_zones)} network zones across "
                f"{pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(all_zones, response, fetch_all_used=True, pagination_info=pagination_info)
        else:
            logger.info(f"Successfully retrieved {len(zones)} network zones")
            return create_paginated_response(zones, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing network zones: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_network_zone(ctx: Context, zone_id: str) -> dict:
    """Get a network zone by ID from the Okta organization.

    Parameters:
        zone_id (str, required): The ID of the network zone to retrieve

    Returns:
        Dict with success status and network zone details.
    """
    logger.info(f"Getting network zone with ID: {zone_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        zone, _, err = await client.get_network_zone(zone_id)

        if err:
            logger.error(f"Okta API error while getting network zone {zone_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved network zone: {zone_id}")
        return success_response(zone)
    except Exception as e:
        logger.error(f"Exception while getting network zone {zone_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def create_network_zone(
    ctx: Context,
    name: str,
    zone_type: str,
    gateways: Optional[List[Dict[str, str]]] = None,
    proxies: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Create a new network zone in the Okta organization.

    Parameters:
        name (str, required): Name for the zone.
        zone_type (str, required): Type of zone ('IP' or 'DYNAMIC').
        gateways (list, optional): List of gateway IPs/CIDRs. Format: [{"type": "CIDR", "value": "10.0.0.0/8"}]
        proxies (list, optional): List of proxy IPs/CIDRs. Format: [{"type": "CIDR", "value": "10.0.0.0/8"}]

    Returns:
        Dict with success status and created network zone details.
    """
    logger.info("Creating new network zone in Okta organization")
    logger.debug(f"Network zone name: {name}, type: {zone_type}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {"name": name, "type": zone_type}
        if gateways:
            body["gateways"] = gateways
        if proxies:
            body["proxies"] = proxies

        logger.debug("Calling Okta API to create network zone")
        zone, _, err = await client.create_network_zone(body)

        if err:
            logger.error(f"Okta API error while creating network zone: {err}")
            return error_response(str(err))

        logger.info("Successfully created network zone")
        return success_response(zone)
    except Exception as e:
        logger.error(f"Exception while creating network zone: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def update_network_zone(
    ctx: Context,
    zone_id: str,
    name: Optional[str] = None,
    gateways: Optional[List[Dict[str, str]]] = None,
    proxies: Optional[List[Dict[str, str]]] = None,
) -> dict:
    """Update a network zone by ID in the Okta organization.

    Parameters:
        zone_id (str, required): The ID of the network zone to update
        name (str, optional): The new name of the network zone
        gateways (list, optional): List of gateway IPs/CIDRs. Format: [{"type": "CIDR", "value": "10.0.0.0/8"}]
        proxies (list, optional): List of proxy IPs/CIDRs. Format: [{"type": "CIDR", "value": "10.0.0.0/8"}]

    Returns:
        Dict with success status and updated network zone details.
    """
    logger.info(f"Updating network zone with ID: {zone_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if gateways is not None:
            body["gateways"] = gateways
        if proxies is not None:
            body["proxies"] = proxies

        logger.debug(f"Calling Okta API to update network zone {zone_id}")
        zone, _, err = await client.update_network_zone(zone_id, body)

        if err:
            logger.error(f"Okta API error while updating network zone {zone_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully updated network zone: {zone_id}")
        return success_response(zone)
    except Exception as e:
        logger.error(f"Exception while updating network zone {zone_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_network_zone(ctx: Context, zone_id: str) -> dict:
    """Delete a network zone by ID from the Okta organization.

    This tool deletes a network zone by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_network_zone afterward.

    Parameters:
        zone_id (str, required): The ID of the network zone to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for network zone {zone_id}, awaiting confirmation")

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of network zone {zone_id}, please type 'DELETE'"),
            "zone_id": zone_id,
        }
    )


@mcp.tool()
async def confirm_delete_network_zone(ctx: Context, zone_id: str, confirmation: str) -> dict:
    """Confirm and execute network zone deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_network_zone.

    Parameters:
        zone_id (str, required): The ID of the network zone to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for network zone {zone_id}")

    if confirmation != "DELETE":
        logger.warning(f"Network zone deletion cancelled for {zone_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete network zone {zone_id}")

        _, err = await client.delete_network_zone(zone_id)

        if err:
            logger.error(f"Okta API error while deleting network zone {zone_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully deleted network zone: {zone_id}")
        return success_response({"message": f"Network zone {zone_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting network zone {zone_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_network_zone(ctx: Context, zone_id: str) -> dict:
    """Activate a network zone in the Okta organization.

    Parameters:
        zone_id (str, required): The ID of the network zone to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating network zone: {zone_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate network zone {zone_id}")

        _, err = await client.activate_network_zone(zone_id)

        if err:
            logger.error(f"Okta API error while activating network zone {zone_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully activated network zone: {zone_id}")
        return success_response({"message": f"Network zone {zone_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating network zone {zone_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def deactivate_network_zone(ctx: Context, zone_id: str) -> dict:
    """Deactivate a network zone in the Okta organization.

    Parameters:
        zone_id (str, required): The ID of the network zone to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating network zone: {zone_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate network zone {zone_id}")

        _, err = await client.deactivate_network_zone(zone_id)

        if err:
            logger.error(f"Okta API error while deactivating network zone {zone_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully deactivated network zone: {zone_id}")
        return success_response({"message": f"Network zone {zone_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating network zone {zone_id}: {type(e).__name__}: {e}")
        return error_response(str(e))
