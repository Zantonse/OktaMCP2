# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Network zone management tools for Okta MCP Server."""

from okta_mcp_server.tools.network_zones.network_zones import (
    activate_network_zone,
    confirm_delete_network_zone,
    create_network_zone,
    deactivate_network_zone,
    delete_network_zone,
    get_network_zone,
    list_network_zones,
    update_network_zone,
)

__all__ = [
    "activate_network_zone",
    "confirm_delete_network_zone",
    "create_network_zone",
    "deactivate_network_zone",
    "delete_network_zone",
    "get_network_zone",
    "list_network_zones",
    "update_network_zone",
]
