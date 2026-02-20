# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Email domain management tools for Okta."""

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id

# ============================================================================
# Email Domain Operations
# ============================================================================


@mcp.tool()
async def list_email_domains(ctx: Context) -> dict:
    """List all email domains in the Okta organization.

    Returns:
        Dict with list of email domains.
    """
    logger.info("Listing all email domains")
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        domains, _, err = await client.list_email_domains()
        if err:
            logger.error(f"Okta API error while listing email domains: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved {len(domains) if domains else 0} email domains")
        return success_response(domains)
    except Exception as e:
        logger.error(f"Exception while listing email domains: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def get_email_domain(ctx: Context, domain_id: str) -> dict:
    """Get an email domain by ID from the Okta organization.

    Parameters:
        domain_id (str, required): The ID of the email domain to retrieve

    Returns:
        Dict with success status and email domain details.
    """
    logger.info(f"Getting email domain with ID: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)
    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        domain, _, err = await client.get_email_domain(domain_id)

        if err:
            logger.error(f"Okta API error while getting email domain {domain_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved email domain: {domain_id}")
        return success_response(domain)
    except Exception as e:
        logger.error(f"Exception while getting email domain {domain_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_email_domain(ctx: Context, domain: str, display_name: str, user_name: str) -> dict:
    """Create an email domain configuration.

    Parameters:
        domain (str, required): The email domain name (e.g., mail.example.com)
        display_name (str, required): The display name for the email domain
        user_name (str, required): The username for the email domain (e.g., noreply)

    Returns:
        Dict with success status and email domain details.
    """
    logger.info(f"Creating email domain: {domain}")

    if not domain or not domain.strip():
        return error_response("domain is required")

    if not display_name or not display_name.strip():
        return error_response("display_name is required")

    if not user_name or not user_name.strip():
        return error_response("user_name is required")

    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        body = {"domain": domain, "displayName": display_name, "userName": user_name}
        result, _, err = await client.create_email_domain(body)
        if err:
            return error_response(sanitize_error(err))
        return success_response(result)
    except Exception as e:
        return error_response(sanitize_error(e))


@mcp.tool()
def delete_email_domain(ctx: Context, domain_id: str) -> dict:
    """Initiate deletion of an email domain.

    This is a destructive operation that requires confirmation.
    Call confirm_delete_email_domain with the confirmation code to complete the deletion.

    Parameters:
        domain_id (str, required): The ID of the email domain to delete

    Returns:
        Dict with confirmation_required flag and message.
    """
    logger.info(f"Initiating delete for email domain: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)

    return {
        "success": True,
        "confirmation_required": True,
        "message": (
            'To confirm deletion of email domain, call confirm_delete_email_domain '
            'with confirmation="DELETE"'
        ),
    }


@mcp.tool()
async def confirm_delete_email_domain(ctx: Context, domain_id: str, confirmation: str) -> dict:
    """Confirm and complete deletion of an email domain.

    Parameters:
        domain_id (str, required): The ID of the email domain to delete
        confirmation (str, required): Confirmation code. Must be exactly "DELETE"

    Returns:
        Dict with success status.
    """
    logger.info(f"Confirming delete for email domain: {domain_id}")

    valid, err_msg = validate_okta_id(domain_id, "domain_id")
    if not valid:
        return error_response(err_msg)

    if confirmation != "DELETE":
        return error_response('confirmation must be exactly "DELETE"')

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_email_domain(domain_id)

        if err:
            logger.error(f"Okta API error while deleting email domain {domain_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully deleted email domain: {domain_id}")
        return success_response({"message": f"Email domain {domain_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Exception while deleting email domain {domain_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
