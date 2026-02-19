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
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Features Management Operations
# ============================================================================


@mcp.tool()
async def list_features(ctx: Context) -> dict:
    """List all features in the Okta organization.

    Returns:
        Dict with list of features.
    """
    logger.info("Listing features in the organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to list features")

        features, _, err = await client.list_features()

        if err:
            logger.error(f"Okta API error while listing features: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(features) if features else 0} features")
        return success_response(features if features else [])
    except Exception as e:
        logger.error(f"Exception while listing features: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_feature(feature_id: str, ctx: Context) -> dict:
    """Get details for a specific feature.

    Parameters:
        feature_id (str, required): The feature ID.

    Returns:
        Dict with feature details.
    """
    logger.info(f"Getting feature {feature_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        valid, err_msg = validate_okta_id(feature_id, "feature_id")
        if not valid:
            return error_response(err_msg)

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get feature {feature_id}")

        feature, _, err = await client.get_feature(feature_id)

        if err:
            logger.error(f"Okta API error while getting feature {feature_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved feature {feature_id}")
        return success_response(feature)
    except Exception as e:
        logger.error(f"Exception while getting feature {feature_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def enable_feature(feature_id: str, ctx: Context, mode: Optional[str] = None) -> dict:
    """Enable a feature in the Okta organization.

    Parameters:
        feature_id (str, required): The feature ID.
        mode (str, optional): The mode for enabling the feature.

    Returns:
        Dict with enabled feature details.
    """
    logger.info(f"Enabling feature {feature_id}")
    logger.debug(f"Mode: {mode}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        valid, err_msg = validate_okta_id(feature_id, "feature_id")
        if not valid:
            return error_response(err_msg)

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to enable feature {feature_id}")

        feature, _, err = await client.update_feature_lifecycle(feature_id, "enable", mode)

        if err:
            logger.error(f"Okta API error while enabling feature {feature_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully enabled feature {feature_id}")
        return success_response(feature)
    except Exception as e:
        logger.error(f"Exception while enabling feature {feature_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def disable_feature(feature_id: str, ctx: Context, mode: Optional[str] = None) -> dict:
    """Disable a feature in the Okta organization.

    Parameters:
        feature_id (str, required): The feature ID.
        mode (str, optional): The mode for disabling the feature.

    Returns:
        Dict with disabled feature details.
    """
    logger.info(f"Disabling feature {feature_id}")
    logger.debug(f"Mode: {mode}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        valid, err_msg = validate_okta_id(feature_id, "feature_id")
        if not valid:
            return error_response(err_msg)

        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to disable feature {feature_id}")

        feature, _, err = await client.update_feature_lifecycle(feature_id, "disable", mode)

        if err:
            logger.error(f"Okta API error while disabling feature {feature_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully disabled feature {feature_id}")
        return success_response(feature)
    except Exception as e:
        logger.error(f"Exception while disabling feature {feature_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
