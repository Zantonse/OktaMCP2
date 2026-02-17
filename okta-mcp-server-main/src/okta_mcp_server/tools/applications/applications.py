# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from typing import Any, Dict, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.pagination import build_query_params, create_paginated_response, paginate_all_results
from okta_mcp_server.utils.response import error_response, success_response


@mcp.tool()
async def list_applications(
    ctx: Context,
    q: Optional[str] = None,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    filter_expr: Optional[str] = None,
    expand: Optional[str] = None,
    include_non_deleted: Optional[bool] = None,
    fetch_all: bool = False,
) -> dict:
    """List all applications from the Okta organization.

    Parameters:
        q (str, optional): Searches for applications by label, property, or link
        after (str, optional): Specifies the pagination cursor for the next page of results
        limit (int, optional): Specifies the number of results per page (min 20, max 100)
        filter_expr (str, optional): Filters applications by status, user.id, group.id, or credentials.signing.kid
        expand (str, optional): Expands the app user object to include the user's profile or expand the app group
        object to include the group's profile
        include_non_deleted (bool, optional): Include non-deleted applications in the results
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.

    Returns:
        Dict containing:
        - items: List of applications from the Okta organization
        - total_fetched: Number of applications returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing applications from Okta organization")
    logger.debug(f"Query parameters: q='{q}', filter='{filter_expr}', limit={limit}, fetch_all={fetch_all}")

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
        query_params = build_query_params(q=q, filter=filter_expr, after=after, limit=limit)

        if expand:
            query_params["expand"] = expand
        if include_non_deleted is not None:
            query_params["includeNonDeleted"] = include_non_deleted

        logger.debug("Calling Okta API to list applications")
        apps, response, err = await client.list_applications(query_params)

        if err:
            logger.error(f"Okta API error while listing applications: {err}")
            return error_response(str(err))

        if not apps:
            logger.info("No applications found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(apps)} applications")
            all_apps, pagination_info = await paginate_all_results(response, apps)

            logger.info(
                f"Successfully retrieved {len(all_apps)} applications across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(all_apps, response, fetch_all_used=True, pagination_info=pagination_info)
        else:
            logger.info(f"Successfully retrieved {len(apps)} applications")
            return create_paginated_response(apps, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing applications: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_application(ctx: Context, app_id: str, expand: Optional[str] = None) -> dict:
    """Get an application by ID from the Okta organization.

    Parameters:
        app_id (str, required): The ID of the application to retrieve
        expand (str, optional): Expands the app user object to include the user's profile or expand the
        app group object

    Returns:
        Dict with success status and application details.
    """
    logger.info(f"Getting application with ID: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        query_params = {}
        if expand:
            query_params["expand"] = expand

        app, _, err = await client.get_application(app_id, query_params)

        if err:
            logger.error(f"Okta API error while getting application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved application: {app_id}")
        return success_response(app)
    except Exception as e:
        logger.error(f"Exception while getting application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def create_application(ctx: Context, app_config: Dict[str, Any], activate: bool = True) -> dict:
    """Create a new application in the Okta organization.

    Parameters:
        app_config (dict, required): The application configuration including name, label, signOnMode, settings, etc.
        activate (bool, optional): Execute activation lifecycle operation after creation. Defaults to True.

    Returns:
        Dict with success status and created application details.
    """
    logger.info("Creating new application in Okta organization")
    logger.debug(f"Application label: {app_config.get('label', 'N/A')}, name: {app_config.get('name', 'N/A')}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        query_params = {"activate": activate}

        logger.debug("Calling Okta API to create application")
        app, _, err = await client.create_application(app_config, query_params)

        if err:
            logger.error(f"Okta API error while creating application: {err}")
            return error_response(str(err))

        logger.info("Successfully created application")
        return success_response(app)
    except Exception as e:
        logger.error(f"Exception while creating application: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def update_application(ctx: Context, app_id: str, app_config: Dict[str, Any]) -> dict:
    """Update an application by ID in the Okta organization.

    Parameters:
        app_id (str, required): The ID of the application to update
        app_config (dict, required): The updated application configuration

    Returns:
        Dict with success status and updated application details.
    """
    logger.info(f"Updating application with ID: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to update application {app_id}")
        app, _, err = await client.update_application(app_id, app_config)

        if err:
            logger.error(f"Okta API error while updating application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully updated application: {app_id}")
        return success_response(app)
    except Exception as e:
        logger.error(f"Exception while updating application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def delete_application(ctx: Context, app_id: str) -> dict:
    """Delete an application by ID from the Okta organization.

    This tool deletes an application by its ID from the Okta organization, but requires confirmation.

    IMPORTANT: After calling this function, you MUST STOP and wait for the human user to type 'DELETE'
    as confirmation. DO NOT automatically call confirm_delete_application afterward.

    Parameters:
        app_id (str, required): The ID of the application to delete

    Returns:
        Dict containing the confirmation request.
    """
    logger.warning(f"Deletion requested for application {app_id}, awaiting confirmation")

    return success_response(
        {
            "confirmation_required": True,
            "message": f"To confirm deletion of application {app_id}, please type 'DELETE'",
            "app_id": app_id,
        }
    )


@mcp.tool()
async def confirm_delete_application(ctx: Context, app_id: str, confirmation: str) -> dict:
    """Confirm and execute application deletion after receiving confirmation.

    This function MUST ONLY be called after the human user has explicitly typed 'DELETE' as confirmation.
    NEVER call this function automatically after delete_application.

    Parameters:
        app_id (str, required): The ID of the application to delete
        confirmation (str, required): Must be 'DELETE' to confirm deletion

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Processing deletion confirmation for application {app_id}")

    if confirmation != "DELETE":
        logger.warning(f"Application deletion cancelled for {app_id} - incorrect confirmation")
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete application {app_id}")

        _, err = await client.delete_application(app_id)

        if err:
            logger.error(f"Okta API error while deleting application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully deleted application: {app_id}")
        return success_response({"message": f"Application {app_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def activate_application(ctx: Context, app_id: str) -> dict:
    """Activate an application in the Okta organization.

    Parameters:
        app_id (str, required): The ID of the application to activate

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating application: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate application {app_id}")

        _, err = await client.activate_application(app_id)

        if err:
            logger.error(f"Okta API error while activating application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully activated application: {app_id}")
        return success_response({"message": f"Application {app_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def deactivate_application(ctx: Context, app_id: str) -> dict:
    """Deactivate an application in the Okta organization.

    Parameters:
        app_id (str, required): The ID of the application to deactivate

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating application: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate application {app_id}")

        _, err = await client.deactivate_application(app_id)

        if err:
            logger.error(f"Okta API error while deactivating application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully deactivated application: {app_id}")
        return success_response({"message": f"Application {app_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def list_application_users(
    app_id: str,
    ctx: Context,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all users assigned to an application with pagination support.

    Parameters:
        app_id (str, required): The ID of the application.
        fetch_all (bool, optional): If True, auto-fetch all pages. Default: False.
        after (str, optional): Pagination cursor.
        limit (int, optional): Maximum per page (min 20, max 100).

    Returns:
        Dict containing:
        - items: List of users assigned to the application
        - total_fetched: Number of users returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing users for application: {app_id}")
    logger.debug(f"Query parameters: limit={limit}, fetch_all={fetch_all}, after={after}")

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
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list application users")
        users, response, err = await client.list_application_users(app_id, query_params)

        if err:
            logger.error(f"Okta API error while listing application users for {app_id}: {err}")
            return error_response(str(err))

        if not users:
            logger.info(f"No users found assigned to application {app_id}")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(users)} users")
            all_users, pagination_info = await paginate_all_results(response, users)

            logger.info(
                f"Successfully retrieved {len(all_users)} users across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(all_users, response, fetch_all_used=True, pagination_info=pagination_info)
        else:
            logger.info(f"Successfully retrieved {len(users)} users for application {app_id}")
            return create_paginated_response(users, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing application users for {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_application_user(app_id: str, user_id: str, ctx: Context) -> dict:
    """Get a specific user assigned to an application.

    Parameters:
        app_id (str, required): The ID of the application.
        user_id (str, required): The ID of the user to retrieve.

    Returns:
        Dict with success status and user assignment details.
    """
    logger.info(f"Getting user {user_id} for application {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to get application user {user_id} for app {app_id}")
        user, _, err = await client.get_application_user(app_id, user_id)

        if err:
            logger.error(f"Okta API error while getting user {user_id} for application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved user {user_id} for application {app_id}")
        return success_response(user)
    except Exception as e:
        logger.error(f"Exception while getting user {user_id} for application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def assign_user_to_application(
    app_id: str,
    user_id: str,
    ctx: Context,
    app_user_config: Optional[Dict[str, Any]] = None,
) -> dict:
    """Assign a user to an application.

    Parameters:
        app_id (str, required): The application ID.
        user_id (str, required): The user ID to assign.
        app_user_config (dict, optional): Additional config like credentials or profile.

    Returns:
        Dict with success status and assignment details.
    """
    logger.info(f"Assigning user {user_id} to application {app_id}")
    logger.debug(f"App user config: {app_user_config}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"id": user_id}
        if app_user_config:
            body.update(app_user_config)

        logger.debug(f"Calling Okta API to assign user {user_id} to application {app_id}")
        user, _, err = await client.assign_user_to_application(app_id, body)

        if err:
            logger.error(f"Okta API error while assigning user {user_id} to application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully assigned user {user_id} to application {app_id}")
        return success_response(user)
    except Exception as e:
        logger.error(f"Exception while assigning user {user_id} to application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def remove_user_from_application(app_id: str, user_id: str, ctx: Context) -> dict:
    """Remove a user from an application.

    Parameters:
        app_id (str, required): The application ID.
        user_id (str, required): The user ID to remove.

    Returns:
        Dict with success status and result of the removal operation.
    """
    logger.info(f"Removing user {user_id} from application {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to remove user {user_id} from application {app_id}")
        _, err = await client.delete_application_user(app_id, user_id)

        if err:
            logger.error(f"Okta API error while removing user {user_id} from application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully removed user {user_id} from application {app_id}")
        return success_response({"message": f"User {user_id} removed from application {app_id} successfully"})
    except Exception as e:
        logger.error(f"Exception while removing user {user_id} from application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def list_application_groups(
    app_id: str,
    ctx: Context,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all groups assigned to an application with pagination support.

    Parameters:
        app_id (str, required): The ID of the application.
        fetch_all (bool, optional): If True, auto-fetch all pages. Default: False.
        after (str, optional): Pagination cursor.
        limit (int, optional): Maximum per page (min 20, max 100).

    Returns:
        Dict containing:
        - items: List of groups assigned to the application
        - total_fetched: Number of groups returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info(f"Listing groups for application: {app_id}")
    logger.debug(f"Query parameters: limit={limit}, fetch_all={fetch_all}, after={after}")

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
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list application groups")
        groups, response, err = await client.list_application_group_assignments(app_id, query_params)

        if err:
            logger.error(f"Okta API error while listing application groups for {app_id}: {err}")
            return error_response(str(err))

        if not groups:
            logger.info(f"No groups found assigned to application {app_id}")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

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
            logger.info(f"Successfully retrieved {len(groups)} groups for application {app_id}")
            return create_paginated_response(groups, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing application groups for {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_application_group(app_id: str, group_id: str, ctx: Context) -> dict:
    """Get a specific group assigned to an application.

    Parameters:
        app_id (str, required): The ID of the application.
        group_id (str, required): The ID of the group to retrieve.

    Returns:
        Dict with success status and group assignment details.
    """
    logger.info(f"Getting group {group_id} for application {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to get application group {group_id} for app {app_id}")
        group, _, err = await client.get_application_group_assignment(app_id, group_id)

        if err:
            logger.error(f"Okta API error while getting group {group_id} for application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved group {group_id} for application {app_id}")
        return success_response(group)
    except Exception as e:
        logger.error(f"Exception while getting group {group_id} for application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def assign_group_to_application(app_id: str, group_id: str, ctx: Context) -> dict:
    """Assign a group to an application.

    Parameters:
        app_id (str, required): The application ID.
        group_id (str, required): The group ID to assign.

    Returns:
        Dict with success status and assignment details.
    """
    logger.info(f"Assigning group {group_id} to application {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to assign group {group_id} to application {app_id}")
        group, _, err = await client.create_application_group_assignment(app_id, group_id, {})

        if err:
            logger.error(f"Okta API error while assigning group {group_id} to application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully assigned group {group_id} to application {app_id}")
        return success_response(group)
    except Exception as e:
        logger.error(f"Exception while assigning group {group_id} to application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def remove_group_from_application(app_id: str, group_id: str, ctx: Context) -> dict:
    """Remove a group from an application.

    Parameters:
        app_id (str, required): The application ID.
        group_id (str, required): The group ID to remove.

    Returns:
        Dict with success status and result of the removal operation.
    """
    logger.info(f"Removing group {group_id} from application {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to remove group {group_id} from application {app_id}")
        _, err = await client.delete_application_group_assignment(app_id, group_id)

        if err:
            logger.error(f"Okta API error while removing group {group_id} from application {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully removed group {group_id} from application {app_id}")
        return success_response({"message": f"Group {group_id} removed from application {app_id} successfully"})
    except Exception as e:
        logger.error(f"Exception while removing group {group_id} from application {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))
