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
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Brand Management Operations
# ============================================================================


@mcp.tool()
async def list_brands(ctx: Context) -> dict:
    """List all brands in the Okta organization.

    Returns:
        Dict with list of brands.
    """
    logger.info("Listing all brands")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        brands, _, err = await client.list_brands()
        if err:
            logger.error(f"Okta API error while listing brands: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(brands) if brands else 0} brands")
        return success_response(brands)
    except Exception as e:
        logger.error(f"Exception while listing brands: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_brand(brand_id: str, ctx: Context) -> dict:
    """Get a brand by ID from the Okta organization.

    Parameters:
        brand_id (str, required): The ID of the brand to retrieve

    Returns:
        Dict with success status and brand details.
    """
    logger.info(f"Getting brand with ID: {brand_id}")

    valid, err_msg = validate_okta_id(brand_id, "brand_id")
    if not valid:
        return error_response(err_msg)
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        brand, _, err = await client.get_brand(brand_id)

        if err:
            logger.error(f"Okta API error while getting brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved brand: {brand_id}")
        return success_response(brand)
    except Exception as e:
        logger.error(f"Exception while getting brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_brand(brand_id: str, ctx: Context, brand_config: Optional[Dict[str, Any]] = None) -> dict:
    """Update a brand in the Okta organization.

    Parameters:
        brand_id (str, required): The ID of the brand to update
        brand_config (dict, optional): Brand configuration including:
            - name (str): Brand name
            - custom_privacy_policy_url (str): URL to custom privacy policy
            - remove_powered_by_okta (bool): Whether to remove "Powered by Okta" branding

    Returns:
        Dict with success status and updated brand details.
    """
    logger.info(f"Updating brand with ID: {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        body = brand_config or {}

        logger.debug(f"Calling Okta API to update brand {brand_id}")
        brand, _, err = await client.update_brand(brand_id, body)

        if err:
            logger.error(f"Okta API error while updating brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated brand: {brand_id}")
        return success_response(brand)
    except Exception as e:
        logger.error(f"Exception while updating brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Brand Theme Operations
# ============================================================================


@mcp.tool()
async def list_brand_themes(brand_id: str, ctx: Context) -> dict:
    """List all themes for a brand in the Okta organization.

    Parameters:
        brand_id (str, required): The ID of the brand

    Returns:
        Dict with list of themes for the brand.
    """
    logger.info(f"Listing themes for brand: {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        themes, _, err = await client.list_brand_themes(brand_id)

        if err:
            logger.error(f"Okta API error while listing themes for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(themes) if themes else 0} themes for brand {brand_id}")
        return success_response(themes)
    except Exception as e:
        logger.error(f"Exception while listing themes for brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_brand_theme(brand_id: str, theme_id: str, ctx: Context) -> dict:
    """Get a specific theme for a brand in the Okta organization.

    Parameters:
        brand_id (str, required): The ID of the brand
        theme_id (str, required): The ID of the theme to retrieve

    Returns:
        Dict with success status and theme details.
    """
    logger.info(f"Getting theme {theme_id} for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        theme, _, err = await client.get_brand_theme(brand_id, theme_id)

        if err:
            logger.error(f"Okta API error while getting theme {theme_id} for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved theme {theme_id} for brand {brand_id}")
        return success_response(theme)
    except Exception as e:
        logger.error(f"Exception while getting theme {theme_id} for brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_brand_theme(
    brand_id: str, theme_id: str, ctx: Context, theme_config: Optional[Dict[str, Any]] = None
) -> dict:
    """Update a brand's theme (colors, variants, etc.).

    Parameters:
        brand_id (str, required): The brand ID.
        theme_id (str, required): The theme ID.
        theme_config (dict, optional): Theme configuration including:
            - primary_color_hex (str): Primary color in hex format (#RRGGBB)
            - secondary_color_hex (str): Secondary color in hex format (#RRGGBB)
            - sign_in_page_touch_point_variant (str): Login page variant
            - end_user_dashboard_touch_point_variant (str): Dashboard variant
            - error_page_touch_point_variant (str): Error page variant
            - email_touch_point_variant (str): Email template variant
            - background_image_url (str): URL to background image

    Returns:
        Dict with updated theme details.
    """
    logger.info(f"Updating theme {theme_id} for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        body = theme_config or {}

        logger.debug(f"Calling Okta API to update theme {theme_id} for brand {brand_id}")
        theme, _, err = await client.update_brand_theme(brand_id, theme_id, body)

        if err:
            logger.error(f"Okta API error while updating theme {theme_id} for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated theme {theme_id} for brand {brand_id}")
        return success_response(theme)
    except Exception as e:
        logger.error(f"Exception while updating theme {theme_id} for brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Brand Theme File Upload Operations
# ============================================================================


@mcp.tool()
async def upload_brand_logo(brand_id: str, theme_id: str, logo_file_path: str, ctx: Context) -> dict:
    """Upload a logo image for a brand theme.

    Parameters:
        brand_id (str, required): The brand ID.
        theme_id (str, required): The theme ID.
        logo_file_path (str, required): Path to the logo image file (e.g., PNG, JPG).

    Returns:
        Dict with upload result.

    Note:
        File upload requires proper file format and size constraints.
        Supported formats: PNG, JPG, GIF. Maximum size typically 512KB.
    """
    logger.info(f"Uploading logo for theme {theme_id} in brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        # Attempt to open and upload the file
        logger.debug(f"Opening file from path: {logo_file_path}")
        with open(logo_file_path, "rb") as file:
            logger.debug(f"Calling Okta API to upload logo for theme {theme_id} in brand {brand_id}")
            result, _, err = await client.upload_brand_theme_logo(brand_id, theme_id, file)

            if err:
                logger.error(f"Okta API error while uploading logo for theme {theme_id}: {err}")
                return error_response(sanitize_error(err))

            logger.info(f"Successfully uploaded logo for theme {theme_id} in brand {brand_id}")
            return success_response(result)
    except FileNotFoundError:
        logger.error(f"Logo file not found at path: {logo_file_path}")
        return error_response(f"Logo file not found at path: {logo_file_path}")
    except Exception as e:
        logger.error(
            f"Exception while uploading logo for theme {theme_id} in brand {brand_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def upload_brand_favicon(brand_id: str, theme_id: str, favicon_file_path: str, ctx: Context) -> dict:
    """Upload a favicon image for a brand theme.

    Parameters:
        brand_id (str, required): The brand ID.
        theme_id (str, required): The theme ID.
        favicon_file_path (str, required): Path to the favicon image file (e.g., ICO, PNG).

    Returns:
        Dict with upload result.

    Note:
        File upload requires proper file format and size constraints.
        Supported formats: ICO, PNG. Maximum size typically 256KB.
    """
    logger.info(f"Uploading favicon for theme {theme_id} in brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        # Attempt to open and upload the file
        logger.debug(f"Opening file from path: {favicon_file_path}")
        with open(favicon_file_path, "rb") as file:
            logger.debug(f"Calling Okta API to upload favicon for theme {theme_id} in brand {brand_id}")
            result, _, err = await client.upload_brand_theme_favicon(brand_id, theme_id, file)

            if err:
                logger.error(f"Okta API error while uploading favicon for theme {theme_id}: {err}")
                return error_response(sanitize_error(err))

            logger.info(f"Successfully uploaded favicon for theme {theme_id} in brand {brand_id}")
            return success_response(result)
    except FileNotFoundError:
        logger.error(f"Favicon file not found at path: {favicon_file_path}")
        return error_response(f"Favicon file not found at path: {favicon_file_path}")
    except Exception as e:
        logger.error(
            f"Exception while uploading favicon for theme {theme_id} in brand {brand_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


# ============================================================================
# Brand Email Template Operations
# ============================================================================


@mcp.tool()
async def get_email_template(brand_id: str, template_name: str, ctx: Context) -> dict:
    """Get an email template for a brand.

    Parameters:
        brand_id (str, required): The ID of the brand
        template_name (str, required): The name of the email template.
            Common template names include:
            - UserActivation: User activation email
            - ForgotPassword: Password reset email
            - ChangeEmail: Email change notification
            - ChangePassword: Password change notification
            - NewSignOn: New sign-on notification
            - LowSecurityIpSignOn: Low security IP sign-on notification
            - ThreatDetectionEmail: Threat detection email

    Returns:
        Dict with success status and email template details.
    """
    logger.info(f"Getting email template '{template_name}' for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        template, _, err = await client.get_email_template(brand_id, template_name)

        if err:
            logger.error(f"Okta API error while getting email template '{template_name}' for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved email template '{template_name}' for brand {brand_id}")
        return success_response(template)
    except Exception as e:
        logger.error(
            f"Exception while getting email template '{template_name}' for brand {brand_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_email_template(
    brand_id: str, template_name: str, ctx: Context, template_config: Optional[Dict[str, Any]] = None
) -> dict:
    """Customize an email template for a brand.

    Parameters:
        brand_id (str, required): The ID of the brand
        template_name (str, required): The name of the email template (e.g., UserActivation, ForgotPassword)
        template_config (dict, optional): Email template configuration including:
            - subject (str): Email subject line
            - html_body (str): HTML content of the email body
            - text_body (str): Plain text content of the email body

    Returns:
        Dict with success status and updated email template details.
    """
    logger.info(f"Updating email template '{template_name}' for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        body = template_config or {}

        logger.debug(f"Calling Okta API to update email template '{template_name}' for brand {brand_id}")
        template, _, err = await client.update_email_template(brand_id, template_name, body)

        if err:
            logger.error(f"Okta API error while updating email template '{template_name}' for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated email template '{template_name}' for brand {brand_id}")
        return success_response(template)
    except Exception as e:
        logger.error(
            f"Exception while updating email template '{template_name}' for brand {brand_id}: {type(e).__name__}: {e}"
        )
        return error_response(sanitize_error(e))


# ============================================================================
# Brand Sign-In Page Operations
# ============================================================================


@mcp.tool()
async def get_signin_page(brand_id: str, ctx: Context) -> dict:
    """Get the sign-in page customization for a brand.

    Parameters:
        brand_id (str, required): The ID of the brand

    Returns:
        Dict with success status and sign-in page customization details.
    """
    logger.info(f"Getting sign-in page customization for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        page, _, err = await client.get_sign_in_page(brand_id)

        if err:
            logger.error(f"Okta API error while getting sign-in page for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved sign-in page customization for brand {brand_id}")
        return success_response(page)
    except Exception as e:
        logger.error(f"Exception while getting sign-in page for brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_signin_page(brand_id: str, ctx: Context, page_config: Optional[Dict[str, Any]] = None) -> dict:
    """Customize the sign-in page for a brand.

    Parameters:
        brand_id (str, required): The ID of the brand
        page_config (dict, optional): Sign-in page configuration including:
            - widget_version (str): Version of the Okta sign-in widget
            - custom_code (str): Custom JavaScript or HTML code
            - widget_customizations (dict): Widget-specific customizations

    Returns:
        Dict with success status and updated sign-in page customization details.
    """
    logger.info(f"Updating sign-in page customization for brand {brand_id}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        body = page_config or {}

        logger.debug(f"Calling Okta API to update sign-in page for brand {brand_id}")
        page, _, err = await client.update_sign_in_page(brand_id, body)

        if err:
            logger.error(f"Okta API error while updating sign-in page for brand {brand_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated sign-in page customization for brand {brand_id}")
        return success_response(page)
    except Exception as e:
        logger.error(f"Exception while updating sign-in page for brand {brand_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
