# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""API token management tools for Okta."""

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# API Token Operations
# ============================================================================


@mcp.tool()
async def list_api_tokens(ctx: Context) -> dict:
    """List all API tokens in the Okta organization.

    Returns:
        Dict with list of API tokens.
    """
    logger.info("Listing all API tokens")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        result, _, err = await client.list_api_tokens()
        if err:
            logger.error(f"Okta API error while listing API tokens: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(result) if result else 0} API tokens")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception while listing API tokens: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_api_token(ctx: Context, token_id: str) -> dict:
    """Get details of a specific API token.

    Parameters:
        token_id (str, required): The ID of the API token to retrieve

    Returns:
        Dict with success status and API token details.
    """
    logger.info(f"Getting API token with ID: {token_id}")

    valid, err_msg = validate_okta_id(token_id, "token_id")
    if not valid:
        return error_response(err_msg)
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        token, _, err = await client.get_api_token(token_id)

        if err:
            logger.error(f"Okta API error while getting API token {token_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved API token: {token_id}")
        return success_response(token)
    except Exception as e:
        logger.error(f"Exception while getting API token {token_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
def revoke_api_token(ctx: Context, token_id: str) -> dict:
    """Initiate revocation of an API token.

    This is a destructive operation that requires confirmation.
    Call confirm_revoke_api_token with the confirmation code to complete the revocation.

    Parameters:
        token_id (str, required): The ID of the API token to revoke

    Returns:
        Dict with confirmation_required flag and message.
    """
    logger.info(f"Initiating revoke for API token: {token_id}")

    valid, err_msg = validate_okta_id(token_id, "token_id")
    if not valid:
        return error_response(err_msg)

    return success_response({
        "confirmation_required": True,
        "message": (
            "Are you sure you want to revoke this API token? This action cannot be undone. "
            'To confirm, call confirm_revoke_api_token with confirmation="REVOKE"'
        ),
        "token_id": token_id,
    })


@mcp.tool()
async def confirm_revoke_api_token(ctx: Context, token_id: str, confirmation: str) -> dict:
    """Confirm and complete revocation of an API token.

    Parameters:
        token_id (str, required): The ID of the API token to revoke
        confirmation (str, required): Confirmation code. Must be exactly "REVOKE"

    Returns:
        Dict with success status.
    """
    logger.info(f"Confirming revoke for API token: {token_id}")

    valid, err_msg = validate_okta_id(token_id, "token_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "REVOKE":
        return error_response('confirmation must be exactly "REVOKE"')

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.revoke_api_token(token_id)

        if err:
            logger.error(f"Okta API error while revoking API token {token_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully revoked API token: {token_id}")
        return success_response({"message": f"API token {token_id} revoked successfully"})
    except Exception as e:
        logger.error(f"Exception while revoking API token {token_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
