# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from typing import Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.pagination import build_query_params, create_paginated_response, paginate_all_results
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_limit, validate_okta_id


@mcp.tool()
async def list_groups(
    ctx: Context,
    search: str = "",
    filter_expr: Optional[str] = None,
    q: Optional[str] = None,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all the groups from the Okta organization with pagination support.
    If search, filter_expr, or q is specified, it will list only those groups that satisfy the condition.

    Parameters:
        search (str, optional): The value of the search string when searching for some specific set of groups.
        filter_expr (str, optional): A filter string to filter groups by Okta profile attributes.
        q (str, optional): A query string to search groups by Okta profile attributes.
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Pagination cursor for fetching results after this point.
        limit (int, optional): Maximum number of groups to return per page (min 20, max 100).
        The search, filter_expr, and q are performed on group profile attributes.

    Examples:
        For pagination:
        - First call: list_groups(search="profile.name sw \"Engineering\"")
        - Next page: list_groups(search="profile.name sw \"Engineering\"", after="cursor_value")
        - All pages: list_groups(search="profile.name sw \"Engineering\"", fetch_all=True)

    Returns:
        Dict containing:
        - items: List of group objects
        - total_fetched: Number of groups returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing groups from Okta organization")
    logger.debug(
        f"Search: '{search}', Filter: '{filter_expr}', Q: '{q}', fetch_all: {fetch_all}, after: '{after}', limit: {limit}"
    )

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(search=search, filter=filter_expr, q=q, after=after, limit=limit)

        logger.debug("Calling Okta API to list groups")
        groups, response, err = await client.list_groups(query_params)

        if err:
            logger.error(f"Okta API error while listing groups: {err}")
            return error_response(sanitize_error(err))

        if not groups:
            logger.info("No groups found")
            return create_paginated_response([], response, fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(groups)} groups")
            all_groups, pagination_info = await paginate_all_results(response, groups)

            logger.info(
                f"Successfully retrieved {len(all_groups)} groups across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_groups, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(groups)} groups")
            return create_paginated_response(groups, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing groups: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_group(ctx: Context, group_id: str) -> dict:
    """Get a group by ID from the Okta organization

    This tool retrieves a group by its ID from the Okta organization.

    Parameters:
        group_id (str, required): The ID of the group to retrieve.

    Returns:
        Dict with success status and group details.
    """
    logger.info(f"Getting group with ID: {group_id}")

    valid, err_msg = validate_okta_id(group_id, "group_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get group {group_id}")

        group, _, err = await client.get_group(group_id)

        if err:
            logger.error(f"Okta API error while getting group {group_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved group: {group_id}")
        return success_response(group)
    except Exception as e:
        logger.error(f"Exception while getting group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_group(ctx: Context, profile: dict) -> dict:
    """Create a group in the Okta organization.

    This tool creates a new group in the Okta organization with the provided profile.

    Parameters:
        profile (dict, required): The profile of the group to create.

    Returns:
        Dict with success status and created group details.
    """
    logger.info("Creating new group in Okta organization")
    logger.debug(f"Group profile: name={profile.get('name', 'N/A')}, description={profile.get('description', 'N/A')}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        # Wrap the profile in a dict with 'profile' key as required by Okta SDK
        logger.debug("Calling Okta API to create group")

        group, _, err = await client.create_group({"profile": profile})

        if err:
            logger.error(f"Okta API error while creating group: {err}")
            return error_response(sanitize_error(err))

        logger.info(
            f"Successfully created group: {group.id} ({group.profile.name if hasattr(group, 'profile') else 'N/A'})"
        )
        return success_response(group)
    except Exception as e:
        logger.error(f"Exception while creating group: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def delete_group(ctx: Context, group_id: str) -> dict:
    """Delete a group by ID from the Okta organization.

    This tool deletes a group by its ID from the Okta organization, but requires confirmation. Wait for the
    user to confirm the deletion before proceeding.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to type 'DELETE'
    as confirmation. DO NOT automatically call confirm_delete_group afterward.

    Parameters:
        group_id (str, required): The ID of the group to delete.

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for group {group_id}, awaiting confirmation")

    return success_response(
        {
            "confirmation_required": True,
            "message": f"To confirm deletion of group {group_id}, please type 'DELETE'",
            "group_id": group_id,
        }
    )


@mcp.tool()
async def confirm_delete_group(ctx: Context, group_id: str, confirmation: str) -> dict:
    """Confirm and execute group deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_group.

    Parameters:
        group_id (str, required): The ID of the group to delete.
        confirmation (str, required): Must be 'DELETE' to confirm deletion.

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for group {group_id}")

    # Step 3: Check confirmation and delete if correct
    if confirmation != "DELETE":
        logger.warning(f"Group deletion cancelled for {group_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete group {group_id}")

        _, err = await client.delete_group(group_id)

        if err:
            logger.error(f"Okta API error while deleting group {group_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted group: {group_id}")
        return success_response({"message": f"Group {group_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_group(ctx: Context, group_id: str, profile: dict) -> dict:
    """Update a group by ID in the Okta organization.

    This tool updates a group by its ID with the provided profile.

    Parameters:
        group_id (str, required): The ID of the group to update.
        profile (dict, required): The new profile for the group.

    Returns:
        Dict with success status and updated group details.
    """
    logger.info(f"Updating group with ID: {group_id}")

    valid, err_msg = validate_okta_id(group_id, "group_id")
    if not valid:
        return error_response(err_msg)
    logger.debug(f"Updated fields: {list(profile.keys())}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        # Wrap the profile in a dict with 'profile' key as required by Okta SDK
        logger.debug(f"Calling Okta API to update group {group_id}")

        group, _, err = await client.update_group(group_id, {"profile": profile})

        if err:
            logger.error(f"Okta API error while updating group {group_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated group: {group_id}")
        return success_response(group)
    except Exception as e:
        logger.error(f"Exception while updating group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def list_group_users(
    ctx: Context,
    group_id: str,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all users in a group by ID from the Okta organization with pagination support.

    This tool retrieves all users in a group by its ID from the Okta organization.

    Parameters:
        group_id (str, required): The ID of the group to retrieve users from.
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Pagination cursor for fetching results after this point.
        limit (int, optional): Maximum number of users to return per page (min 20, max 100).

    Examples:
        For pagination:
        - First call: list_group_users("group_id")
        - Next page: list_group_users("group_id", after="cursor_value")
        - All pages: list_group_users("group_id", fetch_all=True)

    Returns:
        Dict containing:
        - items: List of user objects in the group
        - total_fetched: Number of users returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing users in group: {group_id}")
    logger.debug(f"fetch_all: {fetch_all}, after: '{after}', limit: {limit}")

    # Validate limit parameter range
    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list users in group {group_id}")

        query_params = build_query_params(after=after, limit=limit)
        users, response, err = await client.list_group_users(group_id, query_params)

        if err:
            logger.error(f"Okta API error while listing group users for {group_id}: {err}")
            return error_response(sanitize_error(err))

        if not users:
            logger.info(f"No users found in group {group_id}")
            return create_paginated_response([], response, fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(users)} users in group {group_id}")
            all_users, pagination_info = await paginate_all_results(response, users)

            pages_fetched = pagination_info["pages_fetched"]
            logger.info(
                f"Successfully retrieved {len(all_users)} users from group {group_id} across {pages_fetched} pages"
            )
            return create_paginated_response(all_users, response, fetch_all_used=True, pagination_info=pagination_info)
        else:
            logger.info(f"Successfully retrieved {len(users)} users from group {group_id}")
            return create_paginated_response(users, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing users in group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def list_group_apps(ctx: Context, group_id: str) -> dict:
    """List all applications in a group by ID from the Okta organization.

    This tool retrieves all applications in a group by its ID from the Okta organization.

    Parameters:
        group_id (str, required): The ID of the group to retrieve applications from.

    Returns:
        Dict with success status and list of applications in the group.
    """
    logger.info(f"Listing applications assigned to group: {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list applications for group {group_id}")

        apps, _, err = await client.list_assigned_applications_for_group(group_id)

        if err:
            logger.error(f"Okta API error while listing applications for group {group_id}: {err}")
            return error_response(sanitize_error(err))

        app_count = len(apps) if apps else 0
        logger.info(f"Successfully retrieved {app_count} applications for group {group_id}")

        return success_response([app for app in apps])
    except Exception as e:
        logger.error(f"Exception while listing applications for group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def add_user_to_group(ctx: Context, group_id: str, user_id: str) -> dict:
    """Add a user to a group by ID in the Okta organization.

    This tool adds a user to a group by its ID in the Okta organization.

    Parameters:
        group_id (str, required): The ID of the group to add the user to.
        user_id (str, required): The ID of the user to add to the group.

    Returns:
        Dict with success status and result of the addition operation.
    """
    logger.info(f"Adding user {user_id} to group {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to add user {user_id} to group {group_id}")

        _, err = await client.add_user_to_group(group_id, user_id)

        if err:
            logger.error(f"Okta API error while adding user {user_id} to group {group_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully added user {user_id} to group {group_id}")
        return success_response({"message": "User added to group successfully"})
    except Exception as e:
        logger.error(f"Exception while adding user {user_id} to group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def remove_user_from_group(ctx: Context, group_id: str, user_id: str) -> dict:
    """Remove a user from a group by ID in the Okta organization.

    This tool removes a user from a group by its ID in the Okta organization.

    Parameters:
        group_id (str, required): The ID of the group to remove the user from.
        user_id (str, required): The ID of the user to remove from the group.

    Returns:
        Dict with success status and result of the removal operation.
    """
    logger.info(f"Removing user {user_id} from group {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to remove user {user_id} from group {group_id}")

        _, err = await client.remove_user_from_group(group_id, user_id)

        if err:
            logger.error(f"Okta API error while removing user {user_id} from group {group_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully removed user {user_id} from group {group_id}")
        return success_response({"message": "User removed from group successfully"})
    except Exception as e:
        logger.error(f"Exception while removing user {user_id} from group {group_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
