# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Rate limit settings tools for Okta."""

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error


@mcp.tool()
async def get_rate_limit_settings(ctx: Context) -> dict:
    """Get the rate limit admin notification settings for the organization.

    Returns:
        dict with rate limit notification settings
    """
    logger.info("Retrieving rate limit admin notification settings")
    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        result, _, err = await client.get_rate_limit_settings_admin_notifications()
        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))
        logger.info("Successfully retrieved rate limit settings")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception retrieving rate limit settings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_per_client_rate_limit(ctx: Context) -> dict:
    """Get the per-client rate limit settings for the organization.

    Returns:
        dict with per-client rate limit settings
    """
    logger.info("Retrieving per-client rate limit settings")
    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        result, _, err = await client.get_per_client_rate_limit_settings()
        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))
        logger.info("Successfully retrieved per-client rate limit settings")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception retrieving per-client rate limit settings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_per_client_rate_limit(ctx: Context, settings: dict) -> dict:
    """Update the per-client rate limit settings for the organization.

    Parameters:
        settings: The rate limit settings to apply

    Returns:
        dict with updated per-client rate limit settings
    """
    logger.info("Updating per-client rate limit settings")

    if not settings or not isinstance(settings, dict):
        return error_response("settings must be a non-empty dictionary")

    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        result, _, err = await client.replace_per_client_rate_limit_settings(settings)
        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))
        logger.info("Successfully updated per-client rate limit settings")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception updating per-client rate limit settings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
