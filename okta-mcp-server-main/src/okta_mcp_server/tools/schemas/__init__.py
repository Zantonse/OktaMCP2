# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Schema management tools for Okta MCP Server."""

from okta_mcp_server.tools.schemas.schemas import (
    add_user_schema_property,
    get_app_user_schema,
    get_user_schema,
    get_user_schema_by_type,
    list_user_types,
    remove_user_schema_property,
    update_app_user_schema,
    update_user_schema_property,
)

__all__ = [
    "add_user_schema_property",
    "get_app_user_schema",
    "get_user_schema",
    "get_user_schema_by_type",
    "list_user_types",
    "remove_user_schema_property",
    "update_app_user_schema",
    "update_user_schema_property",
]
