# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from typing import Any, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response


@mcp.tool()
async def get_user_schema(ctx: Context) -> dict:
    """Get the default user profile schema.

    Returns the default user profile schema including base and custom attributes.

    Returns:
        Dict with the user profile schema.
    """
    logger.info("Getting default user schema")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to get default user schema")
        schema, _, err = await client.get_user_schema("default")

        if err:
            logger.error(f"Okta API error while getting default user schema: {err}")
            return error_response(str(err))

        logger.info("Successfully retrieved default user schema")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while getting default user schema: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_user_schema_by_type(type_id: str, ctx: Context) -> dict:
    """Get schema for a specific user type.

    Retrieves the user profile schema for a specific user type ID.

    Parameters:
        type_id (str, required): The ID of the user type.

    Returns:
        Dict with the user profile schema for the specified type.
    """
    logger.info(f"Getting user schema for type: {type_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get user schema for type {type_id}")
        schema, _, err = await client.get_user_schema(type_id)

        if err:
            logger.error(f"Okta API error while getting user schema for type {type_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved user schema for type {type_id}")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while getting user schema for type {type_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def list_user_types(ctx: Context) -> dict:
    """List all user types.

    Returns a list of all user types configured in the Okta organization.

    Returns:
        Dict with list of user types.
    """
    logger.info("Listing all user types")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to list user types")
        types, _, err = await client.list_user_types()

        if err:
            logger.error(f"Okta API error while listing user types: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved {len(types) if types else 0} user types")
        return success_response(types or [])
    except Exception as e:
        logger.error(f"Exception while listing user types: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def add_user_schema_property(
    property_name: str,
    ctx: Context,
    type_id: str = "default",
    property_config: Optional[dict[str, Any]] = None,
) -> dict:
    """Add a custom attribute to the user schema.

    Adds a new custom property to the user profile schema for a specific user type.

    Parameters:
        property_name (str, required): Name for the custom attribute.
        type_id (str, optional): User type ID. Default: "default".
        property_config (dict, optional): Property configuration including:
            - title (str): Display name for the attribute
            - type (str): Data type (string, boolean, integer, number, array). Default: "string"
            - description (str): Description of the attribute
            - required (bool): Whether the attribute is required
            - minLength (int): Minimum string length
            - maxLength (int): Maximum string length
            - enum (list): Allowed values
            - pattern (str): Regex pattern validation

    Returns:
        Dict with updated schema.
    """
    logger.info(f"Adding custom property '{property_name}' to user schema for type {type_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        config = property_config or {}

        # Build the property definition
        property_def = {
            "title": config.get("title", property_name),
            "type": config.get("type", "string"),
            "description": config.get("description", ""),
        }

        # Add optional fields if present in config
        if "minLength" in config:
            property_def["minLength"] = config["minLength"]
        if "maxLength" in config:
            property_def["maxLength"] = config["maxLength"]
        if "enum" in config:
            property_def["enum"] = config["enum"]
        if "pattern" in config:
            property_def["pattern"] = config["pattern"]

        body = {"definitions": {"custom": {"properties": {property_name: property_def}}}}

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to add property '{property_name}' to user schema")
        schema, _, err = await client.update_user_profile(type_id, body)

        if err:
            logger.error(f"Okta API error while adding property '{property_name}': {err}")
            return error_response(str(err))

        logger.info(f"Successfully added property '{property_name}' to user schema")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while adding property '{property_name}': {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def update_user_schema_property(
    property_name: str,
    ctx: Context,
    type_id: str = "default",
    property_config: Optional[dict[str, Any]] = None,
) -> dict:
    """Update a custom attribute in the user schema.

    Updates an existing custom property in the user profile schema for a specific user type.

    Parameters:
        property_name (str, required): Name of the custom attribute to update.
        type_id (str, optional): User type ID. Default: "default".
        property_config (dict, optional): Updated property configuration including:
            - title (str): Display name for the attribute
            - type (str): Data type (string, boolean, integer, number, array)
            - description (str): Description of the attribute
            - minLength (int): Minimum string length
            - maxLength (int): Maximum string length
            - enum (list): Allowed values
            - pattern (str): Regex pattern validation

    Returns:
        Dict with updated schema.
    """
    logger.info(f"Updating custom property '{property_name}' in user schema for type {type_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        config = property_config or {}

        # Build the property definition
        property_def = {
            "title": config.get("title", property_name),
            "type": config.get("type", "string"),
            "description": config.get("description", ""),
        }

        # Add optional fields if present in config
        if "minLength" in config:
            property_def["minLength"] = config["minLength"]
        if "maxLength" in config:
            property_def["maxLength"] = config["maxLength"]
        if "enum" in config:
            property_def["enum"] = config["enum"]
        if "pattern" in config:
            property_def["pattern"] = config["pattern"]

        body = {"definitions": {"custom": {"properties": {property_name: property_def}}}}

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to update property '{property_name}' in user schema")
        schema, _, err = await client.update_user_profile(type_id, body)

        if err:
            logger.error(f"Okta API error while updating property '{property_name}': {err}")
            return error_response(str(err))

        logger.info(f"Successfully updated property '{property_name}' in user schema")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while updating property '{property_name}': {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def remove_user_schema_property(
    property_name: str,
    ctx: Context,
    type_id: str = "default",
) -> dict:
    """Remove a custom attribute from the user schema.

    Removes a custom property from the user profile schema for a specific user type.

    Parameters:
        property_name (str, required): Name of the custom attribute to remove.
        type_id (str, optional): User type ID. Default: "default".

    Returns:
        Dict with updated schema after removal.
    """
    logger.info(f"Removing custom property '{property_name}' from user schema for type {type_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        # To remove a property, set it to None
        body = {"definitions": {"custom": {"properties": {property_name: None}}}}

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to remove property '{property_name}' from user schema")
        schema, _, err = await client.update_user_profile(type_id, body)

        if err:
            logger.error(f"Okta API error while removing property '{property_name}': {err}")
            return error_response(str(err))

        logger.info(f"Successfully removed property '{property_name}' from user schema")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while removing property '{property_name}': {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def get_app_user_schema(app_id: str, ctx: Context) -> dict:
    """Get app-specific user profile schema.

    Retrieves the user profile schema for a specific application.

    Parameters:
        app_id (str, required): The ID of the application.

    Returns:
        Dict with the app-specific user profile schema.
    """
    logger.info(f"Getting app user schema for app: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get app user schema for app {app_id}")
        schema, _, err = await client.get_application_user_schema(app_id)

        if err:
            logger.error(f"Okta API error while getting app user schema for app {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully retrieved app user schema for app {app_id}")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while getting app user schema for app {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))


@mcp.tool()
async def update_app_user_schema(
    app_id: str,
    ctx: Context,
    schema_config: Optional[dict[str, Any]] = None,
) -> dict:
    """Update app-specific user profile schema.

    Updates the user profile schema for a specific application, including custom properties
    and attribute mappings.

    Parameters:
        app_id (str, required): The ID of the application.
        schema_config (dict, optional): Schema configuration to apply including:
            - definitions (dict): Schema definitions with base and custom properties
            - properties (dict): Property definitions

    Returns:
        Dict with updated app user profile schema.
    """
    logger.info(f"Updating app user schema for app: {app_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        config = schema_config or {}

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to update app user schema for app {app_id}")
        schema, _, err = await client.update_application_user_profile(app_id, config)

        if err:
            logger.error(f"Okta API error while updating app user schema for app {app_id}: {err}")
            return error_response(str(err))

        logger.info(f"Successfully updated app user schema for app {app_id}")
        return success_response(schema)
    except Exception as e:
        logger.error(f"Exception while updating app user schema for app {app_id}: {type(e).__name__}: {e}")
        return error_response(str(e))
