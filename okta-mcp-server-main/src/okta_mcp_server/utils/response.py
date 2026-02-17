# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Standardized response utilities for Okta MCP Server tools."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolResponse:
    """Standardized response structure for all MCP tools.

    Attributes:
        success: Whether the operation was successful
        data: The response data (can be any type)
        error: Error message if operation failed
    """

    success: bool
    data: Any = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert response to dictionary format."""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error is not None:
            result["error"] = self.error
        return result


@dataclass
class PaginatedResponse(ToolResponse):
    """Response structure for paginated results.

    Attributes:
        success: Whether the operation was successful
        data: The list of items
        error: Error message if operation failed
        total_fetched: Number of items returned
        has_more: Whether more results are available
        next_cursor: Cursor for fetching next page
        fetch_all_used: Whether fetch_all was used
        pagination_info: Additional pagination metadata
    """

    total_fetched: int = 0
    has_more: bool = False
    next_cursor: Optional[str] = None
    fetch_all_used: bool = False
    pagination_info: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert paginated response to dictionary format."""
        result = {
            "success": self.success,
            "items": self.data if self.data is not None else [],
            "total_fetched": self.total_fetched,
            "has_more": self.has_more,
            "next_cursor": self.next_cursor,
            "fetch_all_used": self.fetch_all_used,
        }
        if self.error is not None:
            result["error"] = self.error
        if self.pagination_info is not None:
            result["pagination_info"] = self.pagination_info
        return result


def success_response(data: Any = None) -> dict:
    """Create a successful response dict.

    Args:
        data: The response data

    Returns:
        Dict with success=True and data
    """
    return ToolResponse(success=True, data=data).to_dict()


def error_response(error: str, data: Any = None) -> dict:
    """Create an error response dict.

    Args:
        error: The error message
        data: Optional partial data

    Returns:
        Dict with success=False and error message
    """
    return ToolResponse(success=False, data=data, error=error).to_dict()
