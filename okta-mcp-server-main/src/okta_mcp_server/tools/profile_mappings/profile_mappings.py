# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Profile Mapping Operations
# ============================================================================


@mcp.tool()
async def list_profile_mappings(
    ctx: Context,
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    after: Optional[str] = None,
    limit: Optional[int] = None,
) -> dict:
    """List profile mappings in the Okta organization.

    Parameters:
        source_id (str, optional): Filter by source app ID
        target_id (str, optional): Filter by target user type ID
        after (str, optional): Pagination cursor for next page
        limit (int, optional): Maximum number of results to return

    Returns:
        Dict containing success status and list of profile mappings.
    """
    logger.info(
        f"Listing profile mappings (source_id={source_id}, target_id={target_id}, "
        f"after={after}, limit={limit})"
    )
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        query_params = {}
        if source_id:
            query_params["sourceId"] = source_id
        if target_id:
            query_params["targetId"] = target_id
        if after:
            query_params["after"] = after
        if limit:
            query_params["limit"] = str(limit)

        mappings, _, err = await client.list_profile_mappings(query_params)
        if err:
            logger.error(f"Okta API error while listing profile mappings: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(mappings) if mappings else 0} profile mappings")
        return success_response(mappings if mappings else [])
    except Exception as e:
        logger.error(f"Exception while listing profile mappings: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_profile_mapping(ctx: Context, mapping_id: str) -> dict:
    """Get a specific profile mapping by ID.

    Parameters:
        mapping_id (str, required): The ID of the profile mapping to retrieve

    Returns:
        Dict with success status and profile mapping details.
    """
    logger.info(f"Getting profile mapping with ID: {mapping_id}")

    valid, err_msg = validate_okta_id(mapping_id, "mapping_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        mapping, _, err = await client.get_profile_mapping(mapping_id)

        if err:
            logger.error(f"Okta API error while getting profile mapping {mapping_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved profile mapping: {mapping_id}")
        return success_response(mapping)
    except Exception as e:
        logger.error(f"Exception while getting profile mapping {mapping_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def update_profile_mapping(ctx: Context, mapping_id: str, mapping_config: dict) -> dict:
    """Update a profile mapping configuration.

    Parameters:
        mapping_id (str, required): The ID of the profile mapping to update
        mapping_config (dict, required): Profile mapping configuration object

    Returns:
        Dict with success status and updated profile mapping details.
    """
    logger.info(f"Updating profile mapping with ID: {mapping_id}")

    valid, err_msg = validate_okta_id(mapping_id, "mapping_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        mapping, _, err = await client.update_profile_mapping(mapping_id, mapping_config)

        if err:
            logger.error(f"Okta API error while updating profile mapping {mapping_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully updated profile mapping: {mapping_id}")
        return success_response(mapping)
    except Exception as e:
        logger.error(f"Exception while updating profile mapping {mapping_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
