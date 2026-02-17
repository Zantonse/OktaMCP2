# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Trusted origins management tools for Okta MCP Server."""

from okta_mcp_server.tools.trusted_origins.trusted_origins import (
    activate_trusted_origin,
    confirm_delete_trusted_origin,
    create_trusted_origin,
    deactivate_trusted_origin,
    delete_trusted_origin,
    get_trusted_origin,
    list_trusted_origins,
    update_trusted_origin,
)

__all__ = [
    "activate_trusted_origin",
    "confirm_delete_trusted_origin",
    "create_trusted_origin",
    "deactivate_trusted_origin",
    "delete_trusted_origin",
    "get_trusted_origin",
    "list_trusted_origins",
    "update_trusted_origin",
]
