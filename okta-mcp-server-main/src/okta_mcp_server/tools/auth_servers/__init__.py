# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Authorization server management tools for Okta MCP Server."""

from okta_mcp_server.tools.auth_servers.auth_servers import (
    activate_authorization_server,
    confirm_delete_authorization_server,
    create_auth_server_claim,
    create_auth_server_policy,
    create_auth_server_scope,
    create_authorization_server,
    deactivate_authorization_server,
    delete_authorization_server,
    get_authorization_server,
    list_auth_server_claims,
    list_auth_server_policies,
    list_auth_server_scopes,
    list_authorization_servers,
    update_authorization_server,
)

__all__ = [
    "activate_authorization_server",
    "confirm_delete_authorization_server",
    "create_auth_server_claim",
    "create_auth_server_policy",
    "create_auth_server_scope",
    "create_authorization_server",
    "deactivate_authorization_server",
    "delete_authorization_server",
    "get_authorization_server",
    "list_auth_server_claims",
    "list_auth_server_policies",
    "list_auth_server_scopes",
    "list_authorization_servers",
    "update_authorization_server",
]
