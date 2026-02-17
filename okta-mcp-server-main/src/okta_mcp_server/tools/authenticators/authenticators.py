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
from okta_mcp_server.utils.validators import sanitize_error, validate_limit, validate_okta_id

# ============================================================================
# Authenticators CRUD Operations
# ============================================================================


@mcp.tool()
async def list_authenticators(ctx: Context) -> dict:
    """List all authenticators configured in the Okta organization.

    Returns:
        Dict with list of authenticators including their types, names, and statuses.
    """
    logger.info("Listing all authenticators")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug("Calling Okta API to list authenticators")

        authenticators, _, err = await client.list_authenticators()

        if err:
            logger.error(f"Okta API error while listing authenticators: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(authenticators) if authenticators else 0} authenticators")
        return success_response(authenticators if authenticators else [])
    except Exception as e:
        logger.error(f"Exception while listing authenticators: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_authenticator(authenticator_id: str, ctx: Context) -> dict:
    """Get authenticator details and settings.

    Parameters:
        authenticator_id (str, required): The ID of the authenticator to retrieve.

    Returns:
        Dict with authenticator details and settings.
    """
    logger.info(f"Getting authenticator with ID: {authenticator_id}")

    valid, err_msg = validate_okta_id(authenticator_id, "authenticator_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get authenticator {authenticator_id}")

        authenticator, _, err = await client.get_authenticator(authenticator_id)

        if err:
            logger.error(f"Okta API error while getting authenticator {authenticator_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved authenticator: {authenticator_id}")
        return success_response(authenticator)
    except Exception as e:
        logger.error(f"Exception while getting authenticator {authenticator_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Authenticator Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_authenticator(authenticator_id: str, ctx: Context) -> dict:
    """Activate an authenticator for the organization.

    Parameters:
        authenticator_id (str, required): The ID of the authenticator to activate.

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating authenticator: {authenticator_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate authenticator {authenticator_id}")

        _, err = await client.activate_authenticator(authenticator_id)

        if err:
            logger.error(f"Okta API error while activating authenticator {authenticator_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated authenticator: {authenticator_id}")
        return success_response({"message": f"Authenticator {authenticator_id} activated successfully"})
    except Exception as e:
        logger.error(f"Exception while activating authenticator {authenticator_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_authenticator(authenticator_id: str, ctx: Context) -> dict:
    """Deactivate an authenticator for the organization.

    Parameters:
        authenticator_id (str, required): The ID of the authenticator to deactivate.

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating authenticator: {authenticator_id}")

    valid, err_msg = validate_okta_id(authenticator_id, "authenticator_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate authenticator {authenticator_id}")

        _, err = await client.deactivate_authenticator(authenticator_id)

        if err:
            logger.error(f"Okta API error while deactivating authenticator {authenticator_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated authenticator: {authenticator_id}")
        return success_response({"message": f"Authenticator {authenticator_id} deactivated successfully"})
    except Exception as e:
        logger.error(f"Exception while deactivating authenticator {authenticator_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


# ============================================================================
# Authenticator Methods Operations
# ============================================================================


@mcp.tool()
async def list_authenticator_methods(authenticator_id: str, ctx: Context) -> dict:
    """List all methods available for an authenticator.

    Parameters:
        authenticator_id (str, required): The authenticator ID.

    Returns:
        Dict with list of methods (push, totp, signed_nonce, etc.) and their statuses.
    """
    logger.info(f"Listing methods for authenticator: {authenticator_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to list methods for authenticator {authenticator_id}")

        methods, _, err = await client.list_authenticator_methods(authenticator_id)

        if err:
            logger.error(f"Okta API error while listing methods for authenticator {authenticator_id}: {err}")
            return error_response(sanitize_error(err))

        retrieved_count = len(methods) if methods else 0
        logger.info(f"Successfully retrieved {retrieved_count} methods for authenticator {authenticator_id}")
        return success_response(methods if methods else [])
    except Exception as e:
        logger.error(f"Exception while listing methods for authenticator {authenticator_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_authenticator_method(authenticator_id: str, method_type: str, ctx: Context) -> dict:
    """Get authenticator method details and settings.

    Parameters:
        authenticator_id (str, required): The authenticator ID.
        method_type (str, required): The method type (push, totp, signed_nonce, etc.).

    Returns:
        Dict with method details and settings.
    """
    logger.info(f"Getting method {method_type} for authenticator {authenticator_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to get method {method_type} for authenticator {authenticator_id}")

        method, _, err = await client.get_authenticator_method(authenticator_id, method_type)

        if err:
            logger.error(
                f"Okta API error while getting method {method_type} for authenticator {authenticator_id}: {err}"
            )
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved method {method_type} for authenticator {authenticator_id}")
        return success_response(method)
    except Exception as e:
        exc_name = type(e).__name__
        logger.error(
            f"Exception while getting method {method_type} for authenticator {authenticator_id}: {exc_name}: {e}"
        )
        return error_response(sanitize_error(e))


# ============================================================================
# Authenticator Method Lifecycle Operations
# ============================================================================


@mcp.tool()
async def activate_authenticator_method(authenticator_id: str, method_type: str, ctx: Context) -> dict:
    """Activate a method for an authenticator.

    Parameters:
        authenticator_id (str, required): The authenticator ID.
        method_type (str, required): The method type to activate (push, totp, signed_nonce, etc.).

    Returns:
        Dict with success status and result of the activation operation.
    """
    logger.info(f"Activating method {method_type} for authenticator {authenticator_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to activate method {method_type} for authenticator {authenticator_id}")

        _, err = await client.activate_authenticator_method(authenticator_id, method_type)

        if err:
            logger.error(
                f"Okta API error while activating method {method_type} for authenticator {authenticator_id}: {err}"
            )
            return error_response(sanitize_error(err))

        logger.info(f"Successfully activated method {method_type} for authenticator {authenticator_id}")
        return success_response(
            {"message": f"Method {method_type} for authenticator {authenticator_id} activated successfully"}
        )
    except Exception as e:
        exc_name = type(e).__name__
        logger.error(
            f"Exception while activating method {method_type} for authenticator {authenticator_id}: {exc_name}: {e}"
        )
        return error_response(sanitize_error(e))


@mcp.tool()
async def deactivate_authenticator_method(authenticator_id: str, method_type: str, ctx: Context) -> dict:
    """Deactivate a method for an authenticator.

    Parameters:
        authenticator_id (str, required): The authenticator ID.
        method_type (str, required): The method type to deactivate (push, totp, signed_nonce, etc.).

    Returns:
        Dict with success status and result of the deactivation operation.
    """
    logger.info(f"Deactivating method {method_type} for authenticator {authenticator_id}")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        logger.debug(f"Calling Okta API to deactivate method {method_type} for authenticator {authenticator_id}")

        _, err = await client.deactivate_authenticator_method(authenticator_id, method_type)

        if err:
            logger.error(
                f"Okta API error while deactivating method {method_type} for authenticator {authenticator_id}: {err}"
            )
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deactivated method {method_type} for authenticator {authenticator_id}")
        return success_response(
            {"message": f"Method {method_type} for authenticator {authenticator_id} deactivated successfully"}
        )
    except Exception as e:
        exc_name = type(e).__name__
        logger.error(
            f"Exception while deactivating method {method_type} for authenticator {authenticator_id}: {exc_name}: {e}"
        )
        return error_response(sanitize_error(e))
