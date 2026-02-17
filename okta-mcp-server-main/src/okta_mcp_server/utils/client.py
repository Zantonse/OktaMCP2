# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import keyring
from loguru import logger
from okta.client import Client as OktaClient

from okta_mcp_server import __version__
from okta_mcp_server.utils.auth.auth_manager import SERVICE_NAME, OktaAuthManager
from okta_mcp_server.utils.retry import with_retry


@with_retry(max_attempts=3, min_wait=1, max_wait=10)
async def get_okta_client(manager: OktaAuthManager) -> OktaClient:
    """Initialize and return an Okta client.

    This function is decorated with retry logic to handle transient failures
    during client initialization.

    Args:
        manager: The OktaAuthManager instance for authentication

    Returns:
        Configured OktaClient instance
    """
    logger.debug("Initializing Okta client")
    api_token = keyring.get_password(SERVICE_NAME, "api_token")
    if not await manager.is_valid_token():
        logger.warning("Token is invalid or expired, re-authenticating")
        await manager.authenticate()
        api_token = keyring.get_password(SERVICE_NAME, "api_token")
    if not api_token:
        raise RuntimeError("No API token available after authentication. Check keyring configuration.")
    config = {
        "orgUrl": manager.org_url,
        "token": api_token,
        "authorizationMode": "Bearer",
        "userAgent": f"okta-mcp-server/{__version__}",
    }
    logger.debug(f"Okta client configured for org: {manager.org_url}")
    return OktaClient(config)
