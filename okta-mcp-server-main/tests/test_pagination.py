# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for pagination behavior with fetch_all=True."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MockOktaResponse, MockUser


class TestFetchAllPagination:
    """Tests that fetch_all=True actually traverses pages."""

    @pytest.mark.asyncio
    async def test_list_users_fetch_all_traverses_pages(self, mock_context):
        """list_users with fetch_all=True should return items from all pages."""
        page1_users = [MockUser(), MockUser()]
        page2_users = [MockUser()]

        page2_response = MockOktaResponse(has_next=False)
        page1_response = MockOktaResponse(
            has_next=True,
            next_url="/api/v1/users?after=cursor123",
            next_page_data=(page2_users, page2_response),
        )

        mock_client = AsyncMock()
        mock_client.list_users.return_value = (page1_users, page1_response, None)

        with patch("okta_mcp_server.tools.users.users.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(ctx=mock_context, fetch_all=True)

        assert result["total_fetched"] == 3
        assert result["fetch_all_used"] is True
