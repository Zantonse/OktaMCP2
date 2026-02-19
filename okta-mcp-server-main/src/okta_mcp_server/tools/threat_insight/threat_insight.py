# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import List, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error


@mcp.tool()
async def get_threat_insight_configuration(ctx: Context) -> dict:
    """Get the current ThreatInsight configuration for the Okta organization.

    ThreatInsight detects and blocks malicious IP addresses that are involved
    in credential-based attacks such as credential stuffing, password spraying,
    and brute force attacks.

    Returns:
        Dict containing:
        - action: Current action mode ("none", "audit", or "block")
        - excludeZones: List of network zone IDs excluded from ThreatInsight
        - created: Timestamp when configuration was created
        - lastUpdated: Timestamp of last update
    """
    logger.info("Getting ThreatInsight configuration")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to get ThreatInsight configuration")
        config, _, err = await client.get_current_configuration()

        if err:
            logger.error(f"Okta API error while getting ThreatInsight configuration: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully retrieved ThreatInsight configuration")
        return success_response(config)
    except Exception as e:
        logger.error(f"Exception while getting ThreatInsight configuration: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_threat_insight_configuration(
    ctx: Context,
    action: str,
    exclude_zones: Optional[List[str]] = None,
) -> dict:
    """Update the ThreatInsight configuration for the Okta organization.

    Parameters:
        action (str, required): The action to take when a threat is detected.
            Must be one of: "none" (disabled), "audit" (log only), "block" (block IPs).
        exclude_zones (list, optional): List of network zone IDs to exclude from ThreatInsight evaluation.

    Returns:
        Dict with success status and updated ThreatInsight configuration.
    """
    logger.info(f"Updating ThreatInsight configuration with action: {action}")

    # Validate action parameter
    valid_actions = {"none", "audit", "block"}
    if action not in valid_actions:
        return error_response(f"Invalid action '{action}'. Must be one of: {', '.join(sorted(valid_actions))}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"action": action}
        if exclude_zones is not None:
            body["excludeZones"] = exclude_zones

        logger.debug("Calling Okta API to update ThreatInsight configuration")
        config, _, err = await client.update_configuration(body)

        if err:
            logger.error(f"Okta API error while updating ThreatInsight configuration: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully updated ThreatInsight configuration")
        return success_response(config)
    except Exception as e:
        logger.error(f"Exception while updating ThreatInsight configuration: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
