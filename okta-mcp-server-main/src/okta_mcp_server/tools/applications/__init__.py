# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Application management tools for Okta MCP Server."""

from okta_mcp_server.tools.applications.applications import (
    activate_application,
    assign_group_to_application,
    assign_user_to_application,
    confirm_delete_application,
    create_application,
    deactivate_application,
    delete_application,
    get_application,
    get_application_group,
    get_application_user,
    list_application_groups,
    list_application_users,
    list_applications,
    remove_group_from_application,
    remove_user_from_application,
    update_application,
)

__all__ = [
    "activate_application",
    "assign_group_to_application",
    "assign_user_to_application",
    "confirm_delete_application",
    "create_application",
    "deactivate_application",
    "delete_application",
    "get_application",
    "get_application_group",
    "get_application_user",
    "list_application_groups",
    "list_application_users",
    "list_applications",
    "remove_group_from_application",
    "remove_user_from_application",
    "update_application",
]
