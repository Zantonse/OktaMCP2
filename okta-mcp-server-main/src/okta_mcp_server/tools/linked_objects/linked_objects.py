# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Linked Objects Management Operations
# ============================================================================


@mcp.tool()
async def list_linked_object_definitions(ctx: Context) -> dict:
    """List all linked object definitions in the Okta organization.

    Returns:
        Dict containing success status and list of linked object definitions.
    """
    logger.info("Listing linked object definitions from Okta organization")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        definitions, _, err = await client.list_linked_object_definitions()
        if err:
            logger.error(f"Okta API error while listing linked object definitions: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(definitions) if definitions else 0} linked object definitions")
        return success_response(definitions if definitions else [])
    except Exception as e:
        logger.error(f"Exception while listing linked object definitions: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_linked_object_definition(ctx: Context, linked_object_name: str) -> dict:
    """Get a specific linked object definition by name from the Okta organization.

    Parameters:
        linked_object_name (str, required): The name of the linked object definition to retrieve

    Returns:
        Dict with success status and linked object definition details.
    """
    logger.info(f"Getting linked object definition with name: {linked_object_name}")

    if not linked_object_name or not linked_object_name.strip():
        return error_response("linked_object_name is required")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        definition, _, err = await client.get_linked_object_definition(linked_object_name)

        if err:
            logger.error(f"Okta API error while getting linked object definition {linked_object_name}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved linked object definition: {linked_object_name}")
        return success_response(definition)
    except Exception as e:
        logger.error(
            f"Exception while getting linked object definition {linked_object_name}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_linked_object_definition(
    ctx: Context,
    primary_name: str,
    primary_title: str,
    primary_description: str,
    associated_name: str,
    associated_title: str,
    associated_description: str,
) -> dict:
    """Create a new linked object definition in the Okta organization.

    Parameters:
        primary_name (str, required): The name of the primary linked object
        primary_title (str, required): The display title of the primary linked object
        primary_description (str, required): The description of the primary linked object
        associated_name (str, required): The name of the associated linked object
        associated_title (str, required): The display title of the associated linked object
        associated_description (str, required): The description of the associated linked object

    Returns:
        Dict with success status and created linked object definition details.
    """
    logger.info(
        f"Creating linked object definition with primary_name: {primary_name}, associated_name: {associated_name}"
    )

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        body = {
            "primary": {
                "name": primary_name,
                "title": primary_title,
                "description": primary_description,
                "type": "USER",
            },
            "associated": {
                "name": associated_name,
                "title": associated_title,
                "description": associated_description,
                "type": "USER",
            },
        }

        client = await get_okta_client(manager)
        definition, _, err = await client.add_linked_object_definition(body)

        if err:
            logger.error(f"Okta API error while creating linked object definition: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully created linked object definition with primary_name: {primary_name}")
        return success_response(definition)
    except Exception as e:
        logger.error(f"Exception while creating linked object definition: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_linked_object_definition(ctx: Context, linked_object_name: str) -> dict:
    """Request deletion of a linked object definition (confirmation required).

    IMPORTANT: This is a two-step process. This tool returns a confirmation prompt.
    You must use confirm_delete_linked_object_definition with the confirmation code to actually delete.

    Parameters:
        linked_object_name (str, required): The name of the linked object definition to delete

    Returns:
        Dict with confirmation_required flag and instructions.
    """
    logger.warning(f"Deletion requested for linked object definition {linked_object_name}, awaiting confirmation")

    if not linked_object_name or not linked_object_name.strip():
        return error_response("linked_object_name is required")

    return success_response(
        {
            "confirmation_required": True,
            "message": (
                f"To confirm deletion of linked object definition {linked_object_name}, "
                "please use confirm_delete_linked_object_definition with confirmation='DELETE'"
            ),
            "linked_object_name": linked_object_name,
        }
    )


@mcp.tool()
async def confirm_delete_linked_object_definition(ctx: Context, linked_object_name: str, confirmation: str) -> dict:
    """Confirm and execute linked object definition deletion.

    IMPORTANT: This completes the two-step deletion process initiated by delete_linked_object_definition.
    The confirmation parameter must be exactly 'DELETE' to proceed.

    Parameters:
        linked_object_name (str, required): The name of the linked object definition to delete
        confirmation (str, required): Confirmation code. Must be exactly 'DELETE'

    Returns:
        Dict with success status and deletion confirmation.
    """
    logger.info(f"Processing deletion confirmation for linked object definition {linked_object_name}")

    if not linked_object_name or not linked_object_name.strip():
        return error_response("linked_object_name is required")

    if confirmation != "DELETE":
        logger.warning(
            f"Linked object definition deletion cancelled for {linked_object_name} - incorrect confirmation"
        )
        return error_response("Deletion cancelled. Confirmation 'DELETE' was not provided correctly.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_linked_object_definition(linked_object_name)

        if err:
            logger.error(f"Okta API error while deleting linked object definition {linked_object_name}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted linked object definition {linked_object_name}")
        return success_response({"message": f"Linked object definition {linked_object_name} deleted successfully"})
    except Exception as e:
        logger.error(
            f"Exception while deleting linked object definition {linked_object_name}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_user_linked_objects(ctx: Context, user_id: str, relationship_name: str) -> dict:
    """Get linked objects for a specific user by relationship name.

    Parameters:
        user_id (str, required): The ID of the user
        relationship_name (str, required): The relationship name to retrieve

    Returns:
        Dict with success status and list of linked user objects.
    """
    logger.info(f"Getting linked objects for user {user_id} with relationship {relationship_name}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    if not relationship_name or not relationship_name.strip():
        return error_response("relationship_name is required")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        linked_objects, _, err = await client.get_linked_objects_for_user(user_id, relationship_name)

        if err:
            logger.error(
                f"Okta API error while getting linked objects for user {user_id}: {err}"
            )
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved linked objects for user {user_id}")
        return success_response(linked_objects if linked_objects else [])
    except Exception as e:
        logger.error(
            f"Exception while getting linked objects for user {user_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))
