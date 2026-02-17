# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

from typing import Any, Dict, Optional

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_limit, validate_okta_id

# ============================================================================
# Factors Management Operations
# ============================================================================


@mcp.tool()
async def list_user_factors(user_id: str, ctx: Context) -> dict:
    """List all MFA factors enrolled for a user.

    Parameters:
        user_id (str, required): The user ID.

    Returns:
        Dict with list of enrolled factors.
    """
    logger.info(f"Listing factors for user: {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list factors for user {user_id}")

        factors, _, err = await client.list_factors(user_id)

        if err:
            logger.error(f"Okta API error while listing factors for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(factors) if factors else 0} factors for user {user_id}")
        return success_response(factors if factors else [])
    except Exception as e:
        logger.error(f"Exception while listing factors for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_user_factor(user_id: str, factor_id: str, ctx: Context) -> dict:
    """Get factor details for a specific factor.

    Parameters:
        user_id (str, required): The user ID.
        factor_id (str, required): The factor ID.

    Returns:
        Dict with factor details.
    """
    logger.info(f"Getting factor {factor_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get factor {factor_id} for user {user_id}")

        factor, _, err = await client.get_factor(user_id, factor_id)

        if err:
            logger.error(f"Okta API error while getting factor {factor_id} for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved factor {factor_id} for user {user_id}")
        return success_response(factor)
    except Exception as e:
        logger.error(f"Exception while getting factor {factor_id} for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def enroll_factor(
    user_id: str,
    factor_type: str,
    ctx: Context,
    provider: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> dict:
    """Enroll a new MFA factor for a user.

    Parameters:
        user_id (str, required): The user ID.
        factor_type (str, required): Type of factor (sms, call, totp, push, webauthn, etc.)
        provider (str, optional): Provider name (OKTA, GOOGLE, RSA, etc.)
        profile (dict, optional): Profile info for factor (e.g., {"phoneNumber": "+1-555-123-4567"})

    Returns:
        Dict with enrolled factor details.
    """
    logger.info(f"Enrolling factor type '{factor_type}' for user {user_id}")
    logger.debug(f"Provider: {provider}, Profile: {profile}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"factorType": factor_type}
        if provider:
            body["provider"] = provider
        if profile:
            body["profile"] = profile

        logger.debug(f"Calling Okta API to enroll factor with body: {body}")

        factor, _, err = await client.enroll_factor(user_id, body)

        if err:
            logger.error(f"Okta API error while enrolling factor for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully enrolled factor {factor_type} for user {user_id}")
        return success_response(factor)
    except Exception as e:
        logger.error(f"Exception while enrolling factor for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def activate_factor(
    user_id: str,
    factor_id: str,
    ctx: Context,
    pass_code: Optional[str] = None,
) -> dict:
    """Activate an enrolled factor (e.g., verify SMS code).

    Parameters:
        user_id (str, required): The user ID.
        factor_id (str, required): The factor ID.
        pass_code (str, optional): Passcode to verify for activation.

    Returns:
        Dict with activated factor details.
    """
    logger.info(f"Activating factor {factor_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {}
        if pass_code:
            body["passCode"] = pass_code

        logger.debug(f"Calling Okta API to activate factor with body: {body}")

        factor, _, err = await client.activate_factor(user_id, factor_id, body)

        if err:
            logger.error(f"Okta API error while activating factor {factor_id} for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated factor {factor_id} for user {user_id}")
        return success_response(factor)
    except Exception as e:
        logger.error(f"Exception while activating factor {factor_id} for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def reset_factor(user_id: str, factor_id: str, ctx: Context) -> dict:
    """Reset/remove a factor for a user.

    This tool resets or removes an enrolled MFA factor from a user's account.

    Parameters:
        user_id (str, required): The user ID.
        factor_id (str, required): The factor ID to reset/remove.

    Returns:
        Dict with success status and result of the operation.
    """
    logger.info(f"Resetting factor {factor_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to delete factor {factor_id} for user {user_id}")

        _, err = await client.delete_factor(user_id, factor_id)

        if err:
            logger.error(f"Okta API error while resetting factor {factor_id} for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully reset factor {factor_id} for user {user_id}")
        return success_response({"message": f"Factor {factor_id} has been reset for user {user_id}."})
    except Exception as e:
        logger.error(f"Exception while resetting factor {factor_id} for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def verify_factor(
    user_id: str,
    factor_id: str,
    pass_code: str,
    ctx: Context,
) -> dict:
    """Verify a factor challenge with a passcode.

    Parameters:
        user_id (str, required): The user ID.
        factor_id (str, required): The factor ID.
        pass_code (str, required): The passcode to verify the factor challenge.

    Returns:
        Dict with verification result.
    """
    logger.info(f"Verifying factor {factor_id} for user {user_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body = {"passCode": pass_code}

        logger.debug("Calling Okta API to verify factor with passcode")

        result, _, err = await client.verify_factor(user_id, factor_id, body)

        if err:
            logger.error(f"Okta API error while verifying factor {factor_id} for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully verified factor {factor_id} for user {user_id}")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception while verifying factor {factor_id} for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
