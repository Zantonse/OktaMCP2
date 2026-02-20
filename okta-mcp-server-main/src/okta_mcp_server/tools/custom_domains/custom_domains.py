# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Custom domain management tools for Okta."""

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Custom Domain Operations
# ============================================================================


@mcp.tool()
async def list_custom_domains(ctx: Context) -> dict:
    """List all custom domains in the Okta organization.

    Returns:
        Dict with list of custom domains.
    """
    logger.info("Listing all custom domains")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        domains, _, err = await client.list_custom_domains()
        if err:
            logger.error(f"Okta API error while listing custom domains: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(domains) if domains else 0} custom domains")
        return success_response(domains)
    except Exception as e:
        logger.error(f"Exception while listing custom domains: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_custom_domain(ctx: Context, domain_id: str) -> dict:
    """Get a custom domain by ID from the Okta organization.

    Parameters:
        domain_id (str, required): The ID of the custom domain to retrieve

    Returns:
        Dict with success status and custom domain details.
    """
    logger.info(f"Getting custom domain with ID: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        domain, _, err = await client.get_custom_domain(domain_id)

        if err:
            logger.error(f"Okta API error while getting custom domain {domain_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved custom domain: {domain_id}")
        return success_response(domain)
    except Exception as e:
        logger.error(f"Exception while getting custom domain {domain_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_custom_domain(ctx: Context, domain: str, certificate_source_type: str) -> dict:
    """Create a custom domain configuration.

    Parameters:
        domain (str, required): The domain name (e.g., login.example.com)
        certificate_source_type (str, required): The certificate source type.
            Must be either "OKTA_MANAGED" or "MANUAL"

    Returns:
        Dict with success status and custom domain details.
    """
    logger.info(f"Creating custom domain: {domain}")

    if certificate_source_type not in ("OKTA_MANAGED", "MANUAL"):
        return error_response("certificate_source_type must be 'OKTA_MANAGED' or 'MANUAL'")

    if not domain or not domain.strip():
        return error_response("domain is required")

    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        body = {"domain": domain, "certificateSourceType": certificate_source_type}
        result, _, err = await client.create_custom_domain(body)
        if err:
            return error_response(sanitize_error(err))
        return success_response(result)
    except Exception as e:
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_custom_domain(ctx: Context, domain_id: str) -> dict:
    """Initiate deletion of a custom domain.

    This is a destructive operation that requires confirmation.
    Call confirm_delete_custom_domain with the confirmation code to complete the deletion.

    Parameters:
        domain_id (str, required): The ID of the custom domain to delete

    Returns:
        Dict with confirmation_required flag and message.
    """
    logger.info(f"Initiating delete for custom domain: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)

    return {
        "success": True,
        "confirmation_required": True,
        "message": (
            'To confirm deletion of custom domain, call confirm_delete_custom_domain '
            'with confirmation="DELETE"'
        ),
    }


@mcp.tool()
async def confirm_delete_custom_domain(ctx: Context, domain_id: str, confirmation: str) -> dict:
    """Confirm and complete deletion of a custom domain.

    Parameters:
        domain_id (str, required): The ID of the custom domain to delete
        confirmation (str, required): Confirmation code. Must be exactly "DELETE"

    Returns:
        Dict with success status.
    """
    logger.info(f"Confirming delete for custom domain: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        return error_response('confirmation must be exactly "DELETE"')

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_custom_domain(domain_id)

        if err:
            logger.error(f"Okta API error while deleting custom domain {domain_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted custom domain: {domain_id}")
        return success_response({"message": f"Custom domain {domain_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting custom domain {domain_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def verify_custom_domain(ctx: Context, domain_id: str) -> dict:
    """Verify a custom domain.

    Parameters:
        domain_id (str, required): The ID of the custom domain to verify

    Returns:
        Dict with success status and verification details.
    """
    logger.info(f"Verifying custom domain with ID: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        domain, _, err = await client.verify_custom_domain(domain_id)

        if err:
            logger.error(f"Okta API error while verifying custom domain {domain_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully verified custom domain: {domain_id}")
        return success_response(domain)
    except Exception as e:
        logger.error(f"Exception while verifying custom domain {domain_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
