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
async def list_authorization_servers(
    ctx: Context,
    q: Optional[str] = None,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    fetch_all: bool = False,
) -> dict:
    """List all authorization servers in the Okta organization.

    Parameters:
        q (str, optional): Searches for authorization servers by name
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.

    Returns:
        Dict containing:
        - items: List of authorization servers from the Okta organization
        - total_fetched: Number of authorization servers returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing authorization servers from Okta organization")
    logger.debug(f"Query parameters: q='{q}', limit={limit}, fetch_all={fetch_all}")

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(q=q, after=after, limit=limit)

        logger.debug("Calling Okta API to list authorization servers")
        servers, response, err = await client.list_authorization_servers(query_params)

        if err:
            logger.error(f"Okta API error while listing authorization servers: {err}")
            return error_response(sanitize_error(err))

        if not servers:
            logger.info("No authorization servers found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(servers)} authorization servers")
            all_servers, pagination_info = await paginate_all_results(response, servers)

            logger.info(
                f"Successfully retrieved {len(all_servers)} authorization servers across "
                f"{pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_servers, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(servers)} authorization servers")
            return create_paginated_response(servers, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing authorization servers: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_authorization_server(ctx: Context, auth_server_id: str) -> dict:
    """Get an authorization server by ID from the Okta organization.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to retrieve

    Returns:
        Dict with success status and authorization server details.
    """
    logger.info(f"Getting authorization server with ID: {auth_server_id}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        server, _, err = await client.get_authorization_server(auth_server_id)

        if err:
            logger.error(f"Okta API error while getting authorization server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved authorization server: {auth_server_id}")
        return success_response(server)
    except Exception as e:
        logger.error(f"Exception while getting authorization server {auth_server_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_authorization_server(
    ctx: Context,
    name: str,
    description: Optional[str] = None,
    audiences: Optional[list] = None,
) -> dict:
    """Create a new authorization server in the Okta organization.

    Parameters:
        name (str, required): The name of the authorization server
        description (str, optional): The description of the authorization server
        audiences (list, optional): The audiences that are allowed to use the authorization server

    Returns:
        Dict with success status and created authorization server details.
    """
    logger.info("Creating new authorization server in Okta organization")
    logger.debug(f"Authorization server name: {name}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"name": name}
        if description:
            body["description"] = description
        if audiences:
            body["audiences"] = audiences

        logger.debug("Calling Okta API to create authorization server")
        server, _, err = await client.create_authorization_server(body)

        if err:
            logger.error(f"Okta API error while creating authorization server: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created authorization server")
        return success_response(server)
    except Exception as e:
        logger.error(f"Exception while creating authorization server: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_authorization_server(
    ctx: Context,
    auth_server_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    audiences: Optional[list] = None,
) -> dict:
    """Update an authorization server by ID in the Okta organization.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to update
        name (str, optional): The new name of the authorization server
        description (str, optional): The new description of the authorization server
        audiences (list, optional): The new audiences that are allowed to use the authorization server

    Returns:
        Dict with success status and updated authorization server details.
    """
    logger.info(f"Updating authorization server with ID: {auth_server_id}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if audiences is not None:
            body["audiences"] = audiences

        logger.debug(f"Calling Okta API to update authorization server {auth_server_id}")
        server, _, err = await client.update_authorization_server(auth_server_id, body)

        if err:
            logger.error(f"Okta API error while updating authorization server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated authorization server: {auth_server_id}")
        return success_response(server)
    except Exception as e:
        logger.error(f"Exception while updating authorization server {auth_server_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Deletion (Two-Step Confirmation)
# ============================================================================


@mcp.tool()
def delete_authorization_server(ctx: Context, auth_server_id: str) -> dict:
    """Delete an authorization server by ID from the Okta organization.

    This tool deletes an authorization server by its ID from the Okta organization, but
    requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to
    type 'DELETE' as confirmation. DO NOT automatically call
    confirm_delete_authorization_server afterward.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for authorization server {auth_server_id}, awaiting confirmation")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    return success_response(
        {
            "confirmation_required": True,
            "message": (f"To confirm deletion of authorization server {auth_server_id}, please type 'DELETE'"),
            "auth_server_id": auth_server_id,
        }
    )


@mcp.tool()
async def confirm_delete_authorization_server(ctx: Context, auth_server_id: str, confirmation: str) -> dict:
    """Confirm and execute authorization server deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_authorization_server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for authorization server {auth_server_id}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        logger.warning(f"Authorization server deletion cancelled for {auth_server_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete authorization server {auth_server_id}")

        _, err = await client.delete_authorization_server(auth_server_id)

        if err:
            logger.error(f"Okta API error while deleting authorization server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted authorization server: {auth_server_id}")
        return success_response({"message": f"Authorization server {auth_server_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting authorization server {auth_server_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_authorization_server(ctx: Context, auth_server_id: str) -> dict:
    """Activate an authorization server in the Okta organization.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating authorization server: {auth_server_id}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate authorization server {auth_server_id}")

        _, err = await client.activate_authorization_server(auth_server_id)

        if err:
            logger.error(f"Okta API error while activating authorization server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated authorization server: {auth_server_id}")
        return success_response({"message": f"Authorization server {auth_server_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating authorization server {auth_server_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_authorization_server(ctx: Context, auth_server_id: str) -> dict:
    """Deactivate an authorization server in the Okta organization.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating authorization server: {auth_server_id}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate authorization server {auth_server_id}")

        _, err = await client.deactivate_authorization_server(auth_server_id)

        if err:
            logger.error(f"Okta API error while deactivating authorization server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated authorization server: {auth_server_id}")
        return success_response({"message": f"Authorization server {auth_server_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating authorization server {auth_server_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Policies Operations
# ============================================================================


@mcp.tool()
async def list_auth_server_policies(
    ctx: Context,
    auth_server_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    fetch_all: bool = False,
) -> dict:
    """List all policies for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.

    Returns:
        Dict containing:
        - items: List of policies for the authorization server
        - total_fetched: Number of policies returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing policies for authorization server: {auth_server_id}")
    logger.debug(f"Query parameters: limit={limit}, fetch_all={fetch_all}, after={after}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list authorization server policies")
        policies, response, err = await client.list_authorization_server_policies(auth_server_id, query_params)

        if err:
            logger.error(f"Okta API error while listing policies for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        if not policies:
            logger.info(f"No policies found for authorization server {auth_server_id}")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(policies)} policies")
            all_policies, pagination_info = await paginate_all_results(response, policies)

            logger.info(
                f"Successfully retrieved {len(all_policies)} policies across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_policies, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(policies)} policies for authorization server {auth_server_id}")
            return create_paginated_response(policies, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(
            f"Exception while listing authorization server policies for {auth_server_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_auth_server_policy(
    ctx: Context,
    auth_server_id: str,
    policy_config: Dict[str, Any],
) -> dict:
    """Create a new policy for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        policy_config (dict, required): The policy configuration including type, status,
        name, description, conditions, and rules.

    Returns:
        Dict with success status and created policy details.
    """
    logger.info(f"Creating new policy for authorization server: {auth_server_id}")
    logger.debug(f"Policy name: {policy_config.get('name', 'N/A')}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug("Calling Okta API to create authorization server policy")
        policy, _, err = await client.create_authorization_server_policy(auth_server_id, policy_config)

        if err:
            logger.error(f"Okta API error while creating policy for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created policy for authorization server {auth_server_id}")
        return success_response(policy)
    except Exception as e:
        logger.error(f"Exception while creating authorization server policy: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Scopes Operations
# ============================================================================


@mcp.tool()
async def list_auth_server_scopes(
    ctx: Context,
    auth_server_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    fetch_all: bool = False,
) -> dict:
    """List all scopes for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.

    Returns:
        Dict containing:
        - items: List of scopes for the authorization server
        - total_fetched: Number of scopes returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing scopes for authorization server: {auth_server_id}")
    logger.debug(f"Query parameters: limit={limit}, fetch_all={fetch_all}, after={after}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list authorization server scopes")
        scopes, response, err = await client.list_o_auth2_scopes(auth_server_id, query_params)

        if err:
            logger.error(f"Okta API error while listing scopes for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        if not scopes:
            logger.info(f"No scopes found for authorization server {auth_server_id}")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(scopes)} scopes")
            all_scopes, pagination_info = await paginate_all_results(response, scopes)

            logger.info(
                f"Successfully retrieved {len(all_scopes)} scopes across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_scopes, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(scopes)} scopes for authorization server {auth_server_id}")
            return create_paginated_response(scopes, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(
            f"Exception while listing authorization server scopes for {auth_server_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_auth_server_scope(
    ctx: Context,
    auth_server_id: str,
    name: str,
    description: Optional[str] = None,
    display_name: Optional[str] = None,
    default_scope: bool = False,
) -> dict:
    """Create a new scope for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        name (str, required): The name of the scope
        description (str, optional): The description of the scope
        display_name (str, optional): The display name of the scope
        default_scope (bool, optional): Whether this is a default scope. Default: False.

    Returns:
        Dict with success status and created scope details.
    """
    logger.info(f"Creating new scope for authorization server: {auth_server_id}")
    logger.debug(f"Scope name: {name}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        scope_body = {
            "name": name,
            "default": default_scope,
        }
        if description:
            scope_body["description"] = description
        if display_name:
            scope_body["displayName"] = display_name

        logger.debug("Calling Okta API to create authorization server scope")
        scope, _, err = await client.create_o_auth2_scope(auth_server_id, scope_body)

        if err:
            logger.error(f"Okta API error while creating scope for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created scope for authorization server {auth_server_id}")
        return success_response(scope)
    except Exception as e:
        logger.error(f"Exception while creating authorization server scope: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Claims Operations
# ============================================================================


@mcp.tool()
async def list_auth_server_claims(
    ctx: Context,
    auth_server_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    fetch_all: bool = False,
) -> dict:
    """List all claims for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.

    Returns:
        Dict containing:
        - items: List of claims for the authorization server
        - total_fetched: Number of claims returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing claims for authorization server: {auth_server_id}")
    logger.debug(f"Query parameters: limit={limit}, fetch_all={fetch_all}, after={after}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list authorization server claims")
        claims, response, err = await client.list_o_auth2_claims(auth_server_id, query_params)

        if err:
            logger.error(f"Okta API error while listing claims for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        if not claims:
            logger.info(f"No claims found for authorization server {auth_server_id}")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(claims)} claims")
            all_claims, pagination_info = await paginate_all_results(response, claims)

            logger.info(
                f"Successfully retrieved {len(all_claims)} claims across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_claims, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(claims)} claims for authorization server {auth_server_id}")
            return create_paginated_response(claims, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(
            f"Exception while listing authorization server claims for {auth_server_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_auth_server_claim(
    ctx: Context,
    auth_server_id: str,
    name: str,
    claim_type: str,
    value_type: str,
    value: Optional[str] = None,
    alwaysInclude: bool = False,
) -> dict:
    """Create a new claim for an authorization server.

    Parameters:
        auth_server_id (str, required): The ID of the authorization server
        name (str, required): The name of the claim
        claim_type (str, required): The type of the claim (e.g., 'RESOURCE', 'IDENTITY')
        value_type (str, required): The value type of the claim (e.g., 'EXPRESSION', 'GROUPS')
        value (str, optional): The expression or value of the claim
        alwaysInclude (bool, optional): Whether to always include the claim. Default: False.

    Returns:
        Dict with success status and created claim details.
    """
    logger.info(f"Creating new claim for authorization server: {auth_server_id}")
    logger.debug(f"Claim name: {name}")

    valid, err_msg = validate_okta_id(auth_server_id, "auth_server_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        claim_body = {
            "name": name,
            "claimType": claim_type,
            "valueType": value_type,
            "alwaysIncludeInToken": alwaysInclude,
        }
        if value:
            claim_body["value"] = value

        logger.debug("Calling Okta API to create authorization server claim")
        claim, _, err = await client.create_o_auth2_claim(auth_server_id, claim_body)

        if err:
            logger.error(f"Okta API error while creating claim for auth server {auth_server_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created claim for authorization server {auth_server_id}")
        return success_response(claim)
    except Exception as e:
        logger.error(f"Exception while creating authorization server claim: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
