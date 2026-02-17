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
async def list_users(
    ctx: Context,
    search: str = "",
    filter_expr: Optional[str] = None,
    q: Optional[str] = None,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all the users from the Okta organization with pagination support.
    If search, filter_expr, or q is specified, it will list only those users that satisfy the condition.
    Use after and limit for pagination.
    Use fetch_all=True to automatically fetch all pages of results.
    By default, it will only fetch users whose status is not "DEPROVISIONED".

    Parameters:
        search (str, optional): The value of the search string when searching for some specific set of users.
        filter_expr (str, optional): A filter string to filter users by Okta profile attributes.
        q (str, optional): A query string to search users by Okta profile attributes.
        fetch_all (bool, optional): If True, automatically fetch all pages of results. Default: False.
        after (str, optional): Pagination cursor for fetching results after this point.
        limit (int, optional): Maximum number of users to return per page (min 20, max 100).
        The search, filter_expr, and q are performed on user profile attributes.

    Examples:
        To search users whose organization is Okta use search=profile.organization eq "Okta"
        To search users updated after 06/01/2013 but with a status of LOCKED_OUT or RECOVERY use
        search=lastUpdated gt "2013-06-01T00:00:00.000Z" and (status eq "LOCKED_OUT" or status eq "RECOVERY")

        For pagination:
        - First call: list_users(search="profile.department eq \"Engineering\"")
        - Next page: list_users(search="profile.department eq \"Engineering\"", after="cursor_value")
        - All pages: list_users(search="profile.department eq \"Engineering\"", fetch_all=True)

    Returns:
        Dict containing:
        - items: List of (user.profile, user.id) tuples
        - total_fetched: Number of users returned
        - has_more: Boolean indicating if more results are available
        - next_cursor: Cursor for the next page (if has_more is True)
        - fetch_all_used: Boolean indicating if fetch_all was used
        - pagination_info: Additional pagination metadata (when fetch_all=True)
    """
    logger.info("Listing users from Okta organization")
    logger.debug(
        f"Search: '{search}', Filter: '{filter_expr}', Q: '{q}', fetch_all: {fetch_all}, after: '{after}', limit: {limit}"
    )

    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(search=search, filter=filter_expr, q=q, after=after, limit=limit)

        logger.debug("Calling Okta API to list users")
        users, response, err = await client.list_users(query_params)

        if err:
            logger.error(f"Okta API error while listing users: {err}")
            return error_response(sanitize_error(err))

        if not users:
            logger.info("No users found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        # Convert users to the expected format
        user_items = [(user.profile, user.id) for user in users]

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(users)} users")
            all_users, pagination_info = await paginate_all_results(response, users)
            all_user_items = [(user.profile, user.id) for user in all_users]

            logger.info(
                f"Successfully retrieved {len(all_user_items)} users across {pagination_info['pages_fetched']} pages"
            )
            return create_paginated_response(
                all_user_items, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(user_items)} users")
            return create_paginated_response(user_items, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception while listing users: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_user_profile_attributes(ctx: Context) -> dict:
    """List all user profile attributes supported by your Okta org.
    This is helpful in case you need to check if the user profile attribute is valid.
    The prompt can contain non existent search terms, in which case we should seek clarification from the user
    by listing most similar profile attributes.

    Returns:
        Dict with success status and list of user profile attributes.
    """
    logger.info("Fetching user profile attributes")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Fetching first user to extract profile attributes")

        users, _, err = await client.list_users({"limit": 1})

        if err:
            logger.error(f"Okta API error while fetching profile attributes: {err}")
            return error_response(sanitize_error(err))

        if len(users) > 0:
            attributes = vars(users[0].profile)
            logger.info(f"Successfully retrieved {len(attributes)} profile attributes")
            logger.debug(f"Profile attributes: {list(attributes.keys())}")
            return success_response(attributes)

        logger.warning("No users found in the organization")
        return success_response([])
    except Exception as e:
        logger.error(f"Exception while fetching profile attributes: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_user(ctx: Context, user_id: str) -> dict:
    """Get a user by ID from the Okta organization

    This tool retrieves a user by their ID from the Okta organization.

    Parameters:
        user_id (str, required): The ID of the user to retrieve.

    Returns:
        Dict with success status and user details.
    """
    logger.info(f"Getting user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get user {user_id}")

        user = await client.get_user(user_id)

        logger.info(f"Successfully retrieved user: {user.profile.email if hasattr(user, 'profile') else user_id}")
        return success_response(user)
    except Exception as e:
        logger.error(f"Exception while getting user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_user(ctx: Context, profile: dict) -> dict:
    """Create a user in the Okta organization.

    This tool creates a new user in the Okta organization with the provided profile.

    Parameters:
        profile (dict, required): The profile of the user to create.

    Returns:
        Dict with success status and created user details.
    """
    logger.info("Creating new user in Okta organization")
    logger.debug(f"User profile: email={profile.get('email', 'N/A')}, login={profile.get('login', 'N/A')}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        # Wrap the profile in a dict with 'profile' key as required by Okta SDK
        user_data = {"profile": profile}
        logger.debug("Calling Okta API to create user")

        user, _, err = await client.create_user(user_data)

        if err:
            logger.error(f"Okta API error while creating user: {err}")
            return error_response(sanitize_error(err))

        logger.info(
            f"Successfully created user: {user.id} ({user.profile.email if hasattr(user, 'profile') else 'N/A'})"
        )
        return success_response(user)
    except Exception as e:
        logger.error(f"Exception while creating user: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_user(ctx: Context, user_id: str, profile: dict) -> dict:
    """Update a user in the Okta organization.

    This tool updates an existing user in the Okta organization with the provided profile.

    Parameters:
        user_id (str, required): The ID of the user to update.
        profile (dict, required): The updated profile of the user.

    Returns:
        Dict with success status and updated user details.
    """
    logger.info(f"Updating user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        user_data = {"profile": profile}
        logger.debug(f"Calling Okta API to update user {user_id}")

        user, _, err = await client.update_user(user_id, user_data)

        if err:
            logger.error(f"Okta API error while updating user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated user: {user_id}")
        return success_response(user)
    except Exception as e:
        logger.error(f"Exception while updating user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_user(ctx: Context, user_id: str) -> dict:
    """Deactivates a user from the Okta organization.

    This tool deactivates a user from the Okta organization by their ID.
    Deactivating the user is a prerequisite for deleting the user.

    Parameters:
        user_id (str, required): The ID of the user to delete.

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate user {user_id}")

        _, err = await client.deactivate_user(user_id)

        if err:
            logger.error(f"Okta API error while deactivating user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated user: {user_id}")
        return success_response({"message": f"User {user_id} deactivated successfully."})
    except Exception as e:
        logger.error(f"Exception while deactivating user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def delete_deactivated_user(ctx: Context, user_id: str) -> dict:
    """Delete a user from the Okta organization who has already been deactivated or deprovisioned.

    This tool deletes a user from the Okta organization by their ID who has already been deactivated or deprovisioned.

    Parameters:
        user_id (str, required): The ID of the deactivated or deprovisioned user to delete.

    Returns:
        Dict with success status and result of the deletion operation.
    """
    logger.info(f"Deleting deactivated user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete user {user_id}")

        _, err = await client.deactivate_or_delete_user(user_id)

        if err:
            logger.error(f"Okta API error while deleting user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted user: {user_id}")
        return success_response({"message": f"User {user_id} deleted successfully."})
    except Exception as e:
        logger.error(f"Exception while deleting user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def activate_user(ctx: Context, user_id: str) -> dict:
    """Activates a user in the Okta organization.

    This tool activates a user in the Okta organization from STAGED or PROVISIONED status.
    Activation transitions the user to the ACTIVE status.

    Parameters:
        user_id (str, required): The ID of the user to activate.

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate user {user_id}")

        _, err = await client.activate_user(user_id)

        if err:
            logger.error(f"Okta API error while activating user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated user: {user_id}")
        return success_response({"message": f"User {user_id} activated successfully."})
    except Exception as e:
        logger.error(f"Exception while activating user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def reactivate_user(ctx: Context, user_id: str) -> dict:
    """Reactivates a user in the Okta organization.

    This tool reactivates a user in the Okta organization from DEPROVISIONED status.
    Reactivation transitions the user back to the ACTIVE status.

    Parameters:
        user_id (str, required): The ID of the user to reactivate.

    Returns:
        Dict with success status and result of the reactivation operation.
    """
    logger.info(f"Reactivating user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to reactivate user {user_id}")

        _, err = await client.reactivate_user(user_id)

        if err:
            logger.error(f"Okta API error while reactivating user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully reactivated user: {user_id}")
        return success_response({"message": f"User {user_id} reactivated successfully."})
    except Exception as e:
        logger.error(f"Exception while reactivating user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def suspend_user(ctx: Context, user_id: str) -> dict:
    """Suspends a user in the Okta organization.

    This tool suspends an active user in the Okta organization. Suspension temporarily
    prevents the user from logging in but preserves the user account.

    Parameters:
        user_id (str, required): The ID of the user to suspend.

    Returns:
        Dict with success status and result of the suspension operation.
    """
    logger.info(f"Suspending user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to suspend user {user_id}")

        _, err = await client.suspend_user(user_id)

        if err:
            logger.error(f"Okta API error while suspending user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully suspended user: {user_id}")
        return success_response({"message": f"User {user_id} suspended successfully."})
    except Exception as e:
        logger.error(f"Exception while suspending user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def unsuspend_user(ctx: Context, user_id: str) -> dict:
    """Unsuspends a user in the Okta organization.

    This tool removes the suspension from a suspended user in the Okta organization.
    Unsuspension restores the user's ability to log in.

    Parameters:
        user_id (str, required): The ID of the user to unsuspend.

    Returns:
        Dict with success status and result of the unsuspension operation.
    """
    logger.info(f"Unsuspending user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to unsuspend user {user_id}")

        _, err = await client.unsuspend_user(user_id)

        if err:
            logger.error(f"Okta API error while unsuspending user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully unsuspended user: {user_id}")
        return success_response({"message": f"User {user_id} unsuspended successfully."})
    except Exception as e:
        logger.error(f"Exception while unsuspending user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def unlock_user(ctx: Context, user_id: str) -> dict:
    """Unlocks a user in the Okta organization.

    This tool unlocks a user in the LOCKED_OUT status in the Okta organization,
    allowing them to attempt logging in again.

    Parameters:
        user_id (str, required): The ID of the user to unlock.

    Returns:
        Dict with success status and result of the unlock operation.
    """
    logger.info(f"Unlocking user with ID: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to unlock user {user_id}")

        _, err = await client.unlock_user(user_id)

        if err:
            logger.error(f"Okta API error while unlocking user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully unlocked user: {user_id}")
        return success_response({"message": f"User {user_id} unlocked successfully."})
    except Exception as e:
        logger.error(f"Exception while unlocking user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def expire_password(ctx: Context, user_id: str) -> dict:
    """Expires the password for a user in the Okta organization.

    This tool expires a user's password, requiring them to reset it on their next login.
    The user will be prompted to set a new password when they next attempt to access their account.

    Parameters:
        user_id (str, required): The ID of the user whose password should be expired.

    Returns:
        Dict with success status and result of the expire password operation.
    """
    logger.info(f"Expiring password for user with ID: {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to expire password for user {user_id}")

        _, err = await client.expire_password(user_id)

        if err:
            logger.error(f"Okta API error while expiring password for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully expired password for user: {user_id}")
        return success_response(
            {"message": f"Password for user {user_id} has been expired. User must reset on next login."}
        )
    except Exception as e:
        logger.error(f"Exception while expiring password for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def expire_password_with_temp_password(ctx: Context, user_id: str) -> dict:
    """Expires the password for a user and generates a temporary password in the Okta organization.

    This tool expires a user's password and generates a temporary password that can be used for
    immediate access. The temporary password is included in the response and should be securely
    communicated to the user.

    Parameters:
        user_id (str, required): The ID of the user whose password should be expired.

    Returns:
        Dict with success status, temporary password, and result of the operation.
    """
    logger.info(f"Expiring password and generating temp password for user with ID: {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to expire password and get temporary password for user {user_id}")

        result, _, err = await client.expire_password_and_get_temporary_password(user_id)

        if err:
            logger.error(f"Okta API error while expiring password for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully expired password and generated temp password for user: {user_id}")
        return success_response(
            {
                "temp_password": result.temp_password,
                "message": f"Password expired for user {user_id}. Temporary password has been generated.",
            }
        )
    except Exception as e:
        logger.error(
            f"Exception while expiring password with temp password for user {user_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def reset_password(ctx: Context, user_id: str, send_email: bool = True) -> dict:
    """Resets a user's password in the Okta organization.

    This tool resets a user's password and generates a password reset link. Optionally,
    the reset link can be automatically sent to the user's email address.

    Parameters:
        user_id (str, required): The ID of the user whose password should be reset.
        send_email (bool, optional): Whether to send the password reset link to the user's email. Default: True.

    Returns:
        Dict with success status, reset URL (if send_email is False), and result of the operation.
    """
    logger.info(f"Resetting password for user with ID: {user_id}")
    logger.debug(f"send_email: {send_email}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to reset password for user {user_id}")

        result, _, err = await client.reset_password(user_id, {"sendEmail": send_email})

        if err:
            logger.error(f"Okta API error while resetting password for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully reset password for user: {user_id}")
        response_dict = {"message": f"Password reset initiated for user {user_id}."}
        if result and hasattr(result, "reset_password_url"):
            response_dict["reset_url"] = result.reset_password_url
        return success_response(response_dict)
    except Exception as e:
        logger.error(f"Exception while resetting password for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def list_user_groups(
    ctx: Context,
    user_id: str,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all groups that a user belongs to with pagination support.

    Parameters:
        user_id (str, required): The ID of the user.
        fetch_all (bool, optional): If True, automatically fetch all pages. Default: False.
        after (str, optional): Pagination cursor.
        limit (int, optional): Maximum per page (min 20, max 100).

    Returns:
        Dict containing:
        - items: List of groups
        - total_fetched: Number returned
        - has_more: Boolean for more results
        - next_cursor: Cursor for next page
        - fetch_all_used: Boolean
        - pagination_info: Metadata (when fetch_all=True)
    """
    logger.info(f"Listing groups for user: {user_id}")
    logger.debug(f"fetch_all: {fetch_all}, after: '{after}', limit: {limit}")

    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        query_params = build_query_params(after=after, limit=limit)

        logger.debug("Calling Okta API to list user groups")
        groups, response, err = await client.list_user_groups(user_id, query_params)

        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))

        if not groups:
            logger.info("No groups found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(groups)} groups")
            all_groups, pagination_info = await paginate_all_results(response, groups)
            pages_count = pagination_info["pages_fetched"]
            logger.info(f"Retrieved {len(all_groups)} groups across {pages_count} pages")
            return create_paginated_response(
                all_groups, response, fetch_all_used=True, pagination_info=pagination_info
            )
        else:
            logger.info(f"Successfully retrieved {len(groups)} groups")
            return create_paginated_response(groups, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def list_user_apps(
    ctx: Context,
    user_id: str,
    fetch_all: bool = False,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List all applications linked to a user with pagination support.

    Parameters:
        user_id (str, required): The ID of the user.
        fetch_all (bool, optional): If True, automatically fetch all pages. Default: False.
        after (str, optional): Pagination cursor.
        limit (int, optional): Maximum per page (min 20, max 100).

    Returns:
        Dict containing:
        - items: List of app links
        - total_fetched: Number returned
        - has_more: Boolean for more results
        - next_cursor: Cursor for next page
        - fetch_all_used: Boolean
        - pagination_info: Metadata (when fetch_all=True)
    """
    logger.info(f"Listing apps for user: {user_id}")
    logger.debug(f"fetch_all: {fetch_all}, after: '{after}', limit: {limit}")

    limit, limit_warning = validate_limit(limit)
    if limit_warning:
        logger.warning(limit_warning)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug("Calling Okta API to list user apps")
        apps, response, err = await client.list_app_links(user_id)

        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))

        if not apps:
            logger.info("No apps found")
            return create_paginated_response([], response, fetch_all_used=fetch_all)

        if fetch_all and response and hasattr(response, "has_next") and response.has_next():
            logger.info(f"fetch_all=True, auto-paginating from initial {len(apps)} apps")
            all_apps, pagination_info = await paginate_all_results(response, apps)
            pages_count = pagination_info["pages_fetched"]
            logger.info(f"Retrieved {len(all_apps)} apps across {pages_count} pages")
            return create_paginated_response(all_apps, response, fetch_all_used=True, pagination_info=pagination_info)
        else:
            logger.info(f"Successfully retrieved {len(apps)} apps")
            return create_paginated_response(apps, response, fetch_all_used=fetch_all)

    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
