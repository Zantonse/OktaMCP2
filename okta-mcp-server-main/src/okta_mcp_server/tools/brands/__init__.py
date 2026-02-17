# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Brands management tools for Okta MCP Server."""

from okta_mcp_server.tools.brands.brands import (
    get_brand,
    get_brand_theme,
    get_email_template,
    get_signin_page,
    list_brand_themes,
    list_brands,
    update_brand,
    update_brand_theme,
    update_email_template,
    update_signin_page,
    upload_brand_favicon,
    upload_brand_logo,
)

__all__ = [
    "get_brand",
    "get_brand_theme",
    "get_email_template",
    "get_signin_page",
    "list_brand_themes",
    "list_brands",
    "update_brand",
    "update_brand_theme",
    "update_email_template",
    "update_signin_page",
    "upload_brand_favicon",
    "upload_brand_logo",
]
