# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.  # noqa: E501
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  # noqa: E501
# See the License for the specific language governing permissions and limitations under the License.

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response

# ============================================================================
# Roles Management Operations
# ============================================================================


@mcp.tool()
def list_roles(ctx: Context) -> dict:
    """List all available admin role types.

    Returns:
        Dict with list of role types and their descriptions.
    """
    logger.info("Listing available admin role types")
    roles = [
        {"type": "SUPER_ADMIN", "description": "Super administrator with full access"},
        {"type": "ORG_ADMIN", "description": "Organization administrator"},
        {"type": "APP_ADMIN", "description": "Application administrator (scoped to apps)"},
        {"type": "USER_ADMIN", "description": "User administrator (scoped to groups)"},
        {"type": "HELP_DESK_ADMIN", "description": "Help desk administrator (scoped to groups)"},
        {"type": "READ_ONLY_ADMIN", "description": "Read-only administrator"},
        {"type": "MOBILE_ADMIN", "description": "Mobile administrator"},
        {
            "type": "API_ACCESS_MANAGEMENT_ADMIN",
            "description": "API access management administrator",
        },
        {"type": "REPORT_ADMIN", "description": "Report administrator"},
    ]
    logger.info(f"Successfully retrieved {len(roles)} available admin role types")
    return success_response(roles)


@mcp.tool()
async def list_user_roles(user_id: str, ctx: Context) -> dict:
    """List roles assigned to a user.

    Parameters:
        user_id (str, required): The user ID.

    Returns:
        Dict with list of roles assigned to the user.
    """
    logger.info(f"Listing roles for user: {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list roles for user {user_id}")

        roles, _, err = await client.list_assigned_roles_for_user(user_id)

        if err:
            logger.error(f"Okta API error while listing roles for user {user_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved {len(roles) if roles else 0} roles for user {user_id}")
        return success_response(roles if roles else [])
    except Exception as e:
        logger.error(f"Exception while listing roles for user {user_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def list_group_roles(group_id: str, ctx: Context) -> dict:
    """List roles assigned to a group.

    Parameters:
        group_id (str, required): The group ID.

    Returns:
        Dict with list of roles assigned to the group.
    """
    logger.info(f"Listing roles for group: {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list roles for group {group_id}")

        roles, _, err = await client.list_assigned_roles_for_group(group_id)

        if err:
            logger.error(f"Okta API error while listing roles for group {group_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved {len(roles) if roles else 0} roles for group {group_id}")
        return success_response(roles if roles else [])
    except Exception as e:
        logger.error(f"Exception while listing roles for group {group_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def assign_role_to_user(user_id: str, role_type: str, ctx: Context) -> dict:
    """Assign an admin role to a user.

    Parameters:
        user_id (str, required): The user ID.
        role_type (str, required): The role type to assign (SUPER_ADMIN, ORG_ADMIN, APP_ADMIN, etc).

    Returns:
        Dict with the assigned role details.
    """
    logger.info(f"Assigning role '{role_type}' to user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"type": role_type}

        logger.debug(f"Calling Okta API to assign role with body: {body}")

        role, _, err = await client.assign_role_to_user(user_id, body)

        if err:
            logger.error(f"Okta API error while assigning role '{role_type}' to user {user_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully assigned role '{role_type}' to user {user_id}")
        return success_response(role)
    except Exception as e:
        logger.error(f"Exception while assigning role to user {user_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def unassign_role_from_user(user_id: str, role_id: str, ctx: Context) -> dict:
    """Remove a role from a user.

    Parameters:
        user_id (str, required): The user ID.
        role_id (str, required): The role assignment ID to remove.

    Returns:
        Dict with success status and result of the operation.
    """
    logger.info(f"Removing role {role_id} from user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to unassign role {role_id} from user {user_id}")

        _, err = await client.unassign_role_from_user(user_id, role_id)

        if err:
            logger.error(f"Okta API error while unassigning role {role_id} from user {user_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully unassigned role {role_id} from user {user_id}")
        return success_response({"message": f"Role {role_id} has been removed from user {user_id}."})
    except Exception as e:
        logger.error(f"Exception while unassigning role from user {user_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def assign_role_to_group(group_id: str, role_type: str, ctx: Context) -> dict:
    """Assign an admin role to a group.

    Parameters:
        group_id (str, required): The group ID.
        role_type (str, required): The role type to assign (USER_ADMIN, HELP_DESK_ADMIN, etc).

    Returns:
        Dict with the assigned role details.
    """
    logger.info(f"Assigning role '{role_type}' to group {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"type": role_type}

        logger.debug(f"Calling Okta API to assign role with body: {body}")

        role, _, err = await client.assign_role_to_group(group_id, body)

        if err:
            logger.error(f"Okta API error while assigning role '{role_type}' to group {group_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully assigned role '{role_type}' to group {group_id}")
        return success_response(role)
    except Exception as e:
        logger.error(f"Exception while assigning role to group {group_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def unassign_role_from_group(group_id: str, role_id: str, ctx: Context) -> dict:
    """Remove a role from a group.

    Parameters:
        group_id (str, required): The group ID.
        role_id (str, required): The role assignment ID to remove.

    Returns:
        Dict with success status and result of the operation.
    """
    logger.info(f"Removing role {role_id} from group {group_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to unassign role {role_id} from group {group_id}")

        _, err = await client.unassign_role_from_group(group_id, role_id)

        if err:
            logger.error(f"Okta API error while unassigning role {role_id} from group {group_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully unassigned role {role_id} from group {group_id}")
        return success_response({"message": f"Role {role_id} has been removed from group {group_id}."})
    except Exception as e:
        logger.error(f"Exception while unassigning role from group {group_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def list_user_role_targets(
    user_id: str,
    role_id: str,
    ctx: Context,
    target_type: str = "GROUP",
) -> dict:
    """List targets for a scoped admin role assignment.

    Parameters:
        user_id (str, required): The user ID.
        role_id (str, required): The role assignment ID.
        target_type (str, optional): "GROUP" or "APP". Default: "GROUP".

    Returns:
        Dict with list of targets (groups or apps) for this role.
    """
    logger.info(f"Listing {target_type} targets for role {role_id} assigned to user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        if target_type == "APP":
            logger.debug(f"Calling Okta API to list app targets for role {role_id}")
            targets, _, err = await client.list_application_targets_for_administrator_role_for_user(user_id, role_id)
        else:
            logger.debug(f"Calling Okta API to list group targets for role {role_id}")
            targets, _, err = await client.list_group_targets_for_role(user_id, role_id)

        if err:
            logger.error(f"Okta API error while listing {target_type} targets for role {role_id}: {err}")
            return error_response(str(err))

        logger.info(
            f"Successfully retrieved {len(targets) if targets else 0} {target_type} targets for role {role_id}"
        )
        return success_response(targets if targets else [])
    except Exception as e:
        logger.error(f"Exception while listing role targets: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def add_user_role_target(
    user_id: str,
    role_id: str,
    target_type: str,
    target_id: str,
    ctx: Context,
) -> dict:
    """Add a target (group or app) to a scoped admin role assignment.

    Parameters:
        user_id (str, required): The user ID.
        role_id (str, required): The role assignment ID.
        target_type (str, required): "GROUP" or "APP".
        target_id (str, required): The target ID (group ID or app ID).

    Returns:
        Dict with success status and result of the operation.
    """
    logger.info(f"Adding {target_type} target {target_id} to role {role_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        if target_type == "APP":
            logger.debug(f"Calling Okta API to add app target {target_id} to role {role_id}")
            _, err = await client.add_application_target_to_admin_role_for_user(user_id, role_id, target_id)
        else:
            logger.debug(f"Calling Okta API to add group target {target_id} to role {role_id}")
            _, err = await client.add_group_target_to_role(user_id, role_id, target_id)

        if err:
            logger.error(f"Okta API error while adding {target_type} target {target_id} to role {role_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully added {target_type} target {target_id} to role {role_id}")
        return success_response({"message": f"{target_type} target {target_id} has been added to role {role_id}."})
    except Exception as e:
        logger.error(f"Exception while adding role target: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def remove_user_role_target(
    user_id: str,
    role_id: str,
    target_type: str,
    target_id: str,
    ctx: Context,
) -> dict:
    """Remove a target (group or app) from a scoped admin role assignment.

    Parameters:
        user_id (str, required): The user ID.
        role_id (str, required): The role assignment ID.
        target_type (str, required): "GROUP" or "APP".
        target_id (str, required): The target ID (group ID or app ID).

    Returns:
        Dict with success status and result of the operation.
    """
    logger.info(f"Removing {target_type} target {target_id} from role {role_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        if target_type == "APP":
            logger.debug(f"Calling Okta API to remove app target {target_id} from role {role_id}")
            _, err = await client.remove_application_target_from_administrator_role_for_user(
                user_id, role_id, target_id
            )
        else:
            logger.debug(f"Calling Okta API to remove group target {target_id} from role {role_id}")
            _, err = await client.remove_group_target_from_role(user_id, role_id, target_id)

        if err:
            logger.error(f"Okta API error while removing {target_type} target {target_id} from role {role_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully removed {target_type} target {target_id} from role {role_id}")
        return success_response({"message": f"{target_type} target {target_id} has been removed from role {role_id}."})
    except Exception as e:
        logger.error(f"Exception while removing role target: {type(e).__name__}: {e}")
        return error_response(str(e))
