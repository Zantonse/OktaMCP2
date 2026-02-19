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
from okta_mcp_server.utils.validators import sanitize_error

# ============================================================================
# Get Org Settings
# ============================================================================


@mcp.tool()
async def get_org_settings(ctx: Context) -> dict:
    """Get the organization settings.

    Retrieves the current settings for the Okta organization, including
    company name, website, phone number, and address information.

    Returns:
        Dict containing:
        - id: Organization ID
        - company_name: Organization company name
        - website: Organization website URL
        - phone_number: Organization phone number
        - address: Organization address information
    """
    logger.info("Getting organization settings")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to get organization settings")
        settings, _, err = await client.get_org_settings()

        if err:
            logger.error(f"Okta API error while getting organization settings: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully retrieved organization settings")
        return success_response(settings)
    except Exception as e:
        logger.error(f"Exception while getting organization settings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Update Org Settings
# ============================================================================

@mcp.tool()
async def update_org_settings(ctx: Context, settings: dict) -> dict:
    """Update the organization settings.

    Partially updates the organization settings. Only provided fields
    will be updated; other fields remain unchanged.

    Parameters:
        settings (dict, required): Dictionary containing organization settings
            to update. Supported fields include:
            - companyName: Organization company name
            - website: Organization website URL
            - phoneNumber: Organization phone number
            - address: Organization address information

    Returns:
        Dict with success status and updated organization settings.
    """
    logger.info("Updating organization settings")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to update organization settings: {settings}")
        updated_settings, _, err = await client.partial_update_org_setting(settings)

        if err:
            logger.error(f"Okta API error while updating organization settings: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully updated organization settings")
        return success_response(updated_settings)
    except Exception as e:
        logger.error(f"Exception while updating organization settings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Get Org Contact Types
# ============================================================================

@mcp.tool()
async def get_org_contact_types(ctx: Context) -> dict:
    """Get the list of organization contact types.

    Retrieves the available contact types for the organization.
    These include types such as TECHNICAL and BILLING.

    Returns:
        Dict containing:
        - A list of contact type objects with contactType field
    """
    logger.info("Getting organization contact types")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to get organization contact types")
        contact_types, _, err = await client.get_org_contact_types()

        if err:
            logger.error(f"Okta API error while getting organization contact types: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully retrieved organization contact types")
        return success_response(contact_types)
    except Exception as e:
        logger.error(f"Exception while getting organization contact types: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Get Org Contact User
# ============================================================================

@mcp.tool()
async def get_org_contact_user(ctx: Context, contact_type: str) -> dict:
    """Get the organization contact user for a specific contact type.

    Retrieves the user assigned as the contact for a specific contact type,
    such as TECHNICAL or BILLING.

    Parameters:
        contact_type (str, required): The type of contact. Must be one of:
            - TECHNICAL: Technical contact for the organization
            - BILLING: Billing contact for the organization

    Returns:
        Dict with success status and organization contact user information.
    """
    logger.info(f"Getting organization contact user for contact type: {contact_type}")

    # Validate contact_type parameter
    valid_contact_types = {"TECHNICAL", "BILLING"}
    if contact_type not in valid_contact_types:
        error_msg = (
            f"Invalid contact_type '{contact_type}'. Must be one of: "
            f"{', '.join(sorted(valid_contact_types))}"
        )
        logger.warning(error_msg)
        return error_response(error_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get organization contact user: {contact_type}")
        contact_user, _, err = await client.get_org_contact_user(contact_type)

        if err:
            logger.error(f"Okta API error while getting organization contact user: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved organization contact user for {contact_type}")
        return success_response(contact_user)
    except Exception as e:
        logger.error(f"Exception while getting organization contact user: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
