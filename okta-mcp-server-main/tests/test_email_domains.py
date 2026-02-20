# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta email domains management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListEmailDomains:
    """Tests for list_email_domains function."""

    @pytest.mark.asyncio
    async def test_list_email_domains_success(self, mock_context, mock_okta_client):
        """Test successfully listing all email domains."""
        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import list_email_domains

            result = await list_email_domains(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_email_domains_error(self, mock_context):
        """Test error handling when listing email domains fails."""
        mock_client = AsyncMock()
        mock_client.list_email_domains = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import list_email_domains

            result = await list_email_domains(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetEmailDomain:
    """Tests for get_email_domain function."""

    @pytest.mark.asyncio
    async def test_get_email_domain_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a specific email domain."""
        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import get_email_domain

            result = await get_email_domain(ctx=mock_context, domain_id="emd1abc123")
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "emd1abc123"

    @pytest.mark.asyncio
    async def test_get_email_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import get_email_domain

            result = await get_email_domain(ctx=mock_context, domain_id="")
            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_email_domain_error(self, mock_context):
        """Test error handling when retrieving an email domain fails."""
        mock_client = AsyncMock()
        mock_client.get_email_domain = AsyncMock(return_value=(None, None, "Domain not found"))

        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import get_email_domain

            result = await get_email_domain(ctx=mock_context, domain_id="emd1abc123")
            assert result.get("success") is False
            assert "error" in result


class TestCreateEmailDomain:
    """Tests for create_email_domain function."""

    @pytest.mark.asyncio
    async def test_create_email_domain_success(self, mock_context, mock_okta_client):
        """Test successfully creating an email domain."""
        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import create_email_domain

            result = await create_email_domain(
                ctx=mock_context,
                domain="mail.example.com",
                display_name="Example Mail",
                user_name="noreply",
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_create_email_domain_error(self, mock_context):
        """Test error handling when creating an email domain fails."""
        mock_client = AsyncMock()
        mock_client.create_email_domain = AsyncMock(return_value=(None, None, "Domain already exists"))

        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import create_email_domain

            result = await create_email_domain(
                ctx=mock_context,
                domain="mail.example.com",
                display_name="Example Mail",
                user_name="noreply",
            )
            assert result.get("success") is False
            assert "error" in result


class TestDeleteEmailDomain:
    """Tests for delete_email_domain function."""

    def test_delete_email_domain_confirmation_required(self, mock_context):
        """Test delete_email_domain returns confirmation_required flag."""
        from okta_mcp_server.tools.email_domains.email_domains import delete_email_domain

        result = delete_email_domain(ctx=mock_context, domain_id="emd1abc123")
        assert result.get("success") is True
        assert result.get("confirmation_required") is True
        assert "message" in result

    def test_delete_email_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        from okta_mcp_server.tools.email_domains.email_domains import delete_email_domain

        result = delete_email_domain(ctx=mock_context, domain_id="")
        assert result.get("success") is False
        assert "error" in result


class TestConfirmDeleteEmailDomain:
    """Tests for confirm_delete_email_domain function."""

    @pytest.mark.asyncio
    async def test_confirm_delete_email_domain_success(self, mock_context, mock_okta_client):
        """Test successfully confirming and deleting an email domain."""
        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import confirm_delete_email_domain

            result = await confirm_delete_email_domain(
                ctx=mock_context, domain_id="emd1abc123", confirmation="DELETE"
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_email_domain_wrong_confirmation(self, mock_context):
        """Test error handling with wrong confirmation string."""
        from okta_mcp_server.tools.email_domains.email_domains import confirm_delete_email_domain

        result = await confirm_delete_email_domain(
            ctx=mock_context, domain_id="emd1abc123", confirmation="WRONG"
        )
        assert result.get("success") is False
        assert "error" in result
        assert "DELETE" in result.get("error")

    @pytest.mark.asyncio
    async def test_confirm_delete_email_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        from okta_mcp_server.tools.email_domains.email_domains import confirm_delete_email_domain

        result = await confirm_delete_email_domain(
            ctx=mock_context, domain_id="", confirmation="DELETE"
        )
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_email_domain_error(self, mock_context):
        """Test error handling when deleting an email domain fails."""
        mock_client = AsyncMock()
        mock_client.delete_email_domain = AsyncMock(return_value=(None, "Domain not found"))

        with patch(
            "okta_mcp_server.tools.email_domains.email_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.email_domains.email_domains import confirm_delete_email_domain

            result = await confirm_delete_email_domain(
                ctx=mock_context, domain_id="emd1abc123", confirmation="DELETE"
            )
            assert result.get("success") is False
            assert "error" in result
