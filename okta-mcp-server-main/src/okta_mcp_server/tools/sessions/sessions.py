# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

from typing import Dict

from loguru import logger
from mcp.server.fastmcp import Context

from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client
from okta_mcp_server.utils.response import error_response, success_response
from okta_mcp_server.utils.validators import sanitize_error, validate_okta_id


@mcp.tool()
async def get_session(ctx: Context, session_id: str) -> dict:
    """Get a session by session ID from the Okta organization.

    Parameters:
        session_id (str, required): The ID of the session to retrieve

    Returns:
        Dict with success status and session details.
    """
    logger.info(f"Getting session with ID: {session_id}")

    valid, err_msg = validate_okta_id(session_id, "session_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to get session {session_id}")
        session, _, err = await client.get_session(session_id)

        if err:
            logger.error(f"Okta API error while getting session {session_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully retrieved session: {session_id}")
        return success_response(session)
    except Exception as e:
        logger.error(f"Exception while getting session {session_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def create_session(ctx: Context, session_token: str) -> dict:
    """Create a new session for a user in the Okta organization.

    Parameters:
        session_token (str, required): The session token to use for creating the session

    Returns:
        Dict with success status and created session details.
    """
    logger.info("Creating new session in Okta organization")

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        body: Dict[str, str] = {"sessionToken": session_token}

        logger.debug("Calling Okta API to create session")
        session, _, err = await client.create_session(body)

        if err:
            logger.error(f"Okta API error while creating session: {err}")
            return error_response(sanitize_error(err))

        logger.info("Successfully created session")
        return success_response(session)
    except Exception as e:
        logger.error(f"Exception while creating session: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def refresh_session(ctx: Context, session_id: str) -> dict:
    """Refresh an existing session to extend its lifetime in the Okta organization.

    Parameters:
        session_id (str, required): The ID of the session to refresh

    Returns:
        Dict with success status and refreshed session details.
    """
    logger.info(f"Refreshing session with ID: {session_id}")

    valid, err_msg = validate_okta_id(session_id, "session_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to refresh session {session_id}")
        session, _, err = await client.refresh_session(session_id)

        if err:
            logger.error(f"Okta API error while refreshing session {session_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully refreshed session: {session_id}")
        return success_response(session)
    except Exception as e:
        logger.error(f"Exception while refreshing session {session_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def close_session(ctx: Context, session_id: str) -> dict:
    """Close/revoke a specific session by ID in the Okta organization.

    Parameters:
        session_id (str, required): The ID of the session to close

    Returns:
        Dict with success status and result of the close operation.
    """
    logger.info(f"Closing session with ID: {session_id}")

    valid, err_msg = validate_okta_id(session_id, "session_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to close session {session_id}")
        _, err = await client.close_session(session_id)

        if err:
            logger.error(f"Okta API error while closing session {session_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully closed session: {session_id}")
        return success_response({"message": f"Session {session_id} closed successfully"})
    except Exception as e:
        logger.error(f"Exception while closing session {session_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))


@mcp.tool()
async def revoke_user_sessions(ctx: Context, user_id: str) -> dict:
    """Revoke all sessions for a specific user in the Okta organization.

    Parameters:
        user_id (str, required): The ID of the user whose sessions should be revoked

    Returns:
        Dict with success status and result of the revoke operation.
    """
    logger.info(f"Revoking all sessions for user: {user_id}")

    valid, err_msg = validate_okta_id(user_id, "user_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)

        logger.debug(f"Calling Okta API to revoke all sessions for user {user_id}")
        _, err = await client.revoke_user_sessions(user_id)

        if err:
            logger.error(f"Okta API error while revoking sessions for user {user_id}: {err}")
            return error_response(sanitize_error(err))

        logger.info(f"Successfully revoked all sessions for user: {user_id}")
        return success_response({"message": f"All sessions for user {user_id} revoked successfully"})
    except Exception as e:
        logger.error(f"Exception while revoking sessions for user {user_id}: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
