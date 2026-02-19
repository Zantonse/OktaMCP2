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
async def list_identity_providers(
    ctx: Context,
    q: Optional[str] = None,
    type_filter: Optional[str] = None,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all identity providers in the Okta organization.

    Parameters:
        q (str, optional): Search query for IdP name
        type_filter (str, optional): Filter by IdP type (SAML2, OIDC, GOOGLE, FACEBOOK, etc.)
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)

    Returns:
        Dict containing:
        - items: List of identity providers from the Okta organization
        - total_fetched: Number of identity providers returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing identity providers from Okta organization")
    logger.debug(f"Query parameters: q='{q}', type_filter='{type_filter}', limit={limit}, fetch_all={fetch_all}")

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(q=q, type_filter=type_filter, after=after, limit=limit)

        logger.debug("Calling Okta API to list identity providers")
        providers, response, err = await client.list_identity_providers(query_params)

        if err:
            logger.error(f"Okta API error while listing identity providers: {err}")
            return error_response(sanitize_error(err))

        if not providers:
            logger.info("No identity providers found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(providers)} identity providers")
            all_providers, pagination_info = await paginate_all_results(response, providers)

            logger.info(
                f"Successfully retrieved {len(all_providers)} identity providers across "
                f"{pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_providers, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(providers)} identity providers")
            return create_paginated_response(providers, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing identity providers: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_identity_provider(ctx: Context, idp_id: str) -> dict:
    """Get an identity provider by ID from the Okta organization.

    Parameters:
        idp_id (str, required): The ID of the identity provider to retrieve

    Returns:
        Dict with success status and identity provider details.
    """
    logger.info(f"Getting identity provider with ID: {idp_id}")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        provider, _, err = await client.get_identity_provider(idp_id)

        if err:
            logger.error(f"Okta API error while getting identity provider {idp_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved identity provider: {idp_id}")
        return success_response(provider)
    except Exception as e:
        logger.error(f"Exception while getting identity provider {idp_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_identity_provider(
    ctx: Context,
    name: str,
    idp_type: str,
    protocol: Optional[str] = None,
    policy: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> dict:
    """Create a new identity provider in the Okta organization.

    Parameters:
        name (str, required): The name of the identity provider
        idp_type (str, required): The type of the identity provider (SAML2, OIDC, GOOGLE, FACEBOOK, etc.)
        protocol (dict, optional): The protocol configuration for the identity provider
        policy (dict, optional): The policy configuration for the identity provider
        **kwargs: Additional fields for the identity provider (e.g., endpoints, credentials)

    Returns:
        Dict with success status and created identity provider details.
    """
    logger.info("Creating new identity provider in Okta organization")
    logger.debug(f"Identity provider name: {name}, type: {idp_type}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"type": idp_type, "name": name}
        if protocol:
            body["protocol"] = protocol
        if policy:
            body["policy"] = policy
        body.update(kwargs)

        logger.debug("Calling Okta API to create identity provider")
        provider, _, err = await client.create_identity_provider(body)

        if err:
            logger.error(f"Okta API error while creating identity provider: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created identity provider")
        return success_response(provider)
    except Exception as e:
        logger.error(f"Exception while creating identity provider: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_identity_provider(
    ctx: Context,
    idp_id: str,
    name: Optional[str] = None,
    protocol: Optional[Dict[str, Any]] = None,
    policy: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> dict:
    """Update an identity provider by ID in the Okta organization.

    Parameters:
        idp_id (str, required): The ID of the identity provider to update
        name (str, optional): The new name of the identity provider
        protocol (dict, optional): The new protocol configuration for the identity provider
        policy (dict, optional): The new policy configuration for the identity provider
        **kwargs: Additional fields to update for the identity provider

    Returns:
        Dict with success status and updated identity provider details.
    """
    logger.info(f"Updating identity provider with ID: {idp_id}")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {}
        if name is not None:
            body["name"] = name
        if protocol is not None:
            body["protocol"] = protocol
        if policy is not None:
            body["policy"] = policy
        body.update(kwargs)

        logger.debug(f"Calling Okta API to update identity provider {idp_id}")
        provider, _, err = await client.update_identity_provider(idp_id, body)

        if err:
            logger.error(f"Okta API error while updating identity provider {idp_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated identity provider: {idp_id}")
        return success_response(provider)
    except Exception as e:
        logger.error(f"Exception while updating identity provider {idp_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_identity_provider(ctx: Context, idp_id: str) -> dict:
    """Delete an identity provider by ID from the Okta organization.

    This tool deletes an identity provider by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_identity_provider afterward.

    Parameters:
        idp_id (str, required): The ID of the identity provider to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for identity provider {idp_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of identity provider {idp_id}, please type 'DELETE'"),
            "idp_id": idp_id,
        }
    )


@mcp.tool()
async def confirm_delete_identity_provider(ctx: Context, idp_id: str, confirmation: str) -> dict:
    """Confirm and execute identity provider deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_identity_provider.

    Parameters:
        idp_id (str, required): The ID of the identity provider to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for identity provider {idp_id}")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Identity provider deletion cancelled for {idp_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete identity provider {idp_id}")

        _, err = await client.delete_identity_provider(idp_id)

        if err:
            logger.error(f"Okta API error while deleting identity provider {idp_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted identity provider: {idp_id}")
        return success_response({"message": f"Identity provider {idp_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting identity provider {idp_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_identity_provider(ctx: Context, idp_id: str) -> dict:
    """Activate an identity provider in the Okta organization.

    Parameters:
        idp_id (str, required): The ID of the identity provider to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating identity provider: {idp_id}")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate identity provider {idp_id}")

        _, err = await client.activate_identity_provider(idp_id)

        if err:
            logger.error(f"Okta API error while activating identity provider {idp_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated identity provider: {idp_id}")
        return success_response({"message": f"Identity provider {idp_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating identity provider {idp_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_identity_provider(ctx: Context, idp_id: str) -> dict:
    """Deactivate an identity provider in the Okta organization.

    Parameters:
        idp_id (str, required): The ID of the identity provider to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating identity provider: {idp_id}")

    valid, err_msg = validate_okta_id(idp_id, "idp_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate identity provider {idp_id}")

        _, err = await client.deactivate_identity_provider(idp_id)

        if err:
            logger.error(f"Okta API error while deactivating identity provider {idp_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated identity provider: {idp_id}")
        return success_response({"message": f"Identity provider {idp_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating identity provider {idp_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
