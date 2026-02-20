# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta custom domains management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListCustomDomains:
    """Tests for list_custom_domains function."""

    @pytest.mark.asyncio
    async def test_list_custom_domains_success(self, mock_context, mock_okta_client):
        """Test successfully listing all custom domains."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import list_custom_domains

            result = await list_custom_domains(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_custom_domains_error(self, mock_context):
        """Test error handling when listing custom domains fails."""
        mock_client = AsyncMock()
        mock_client.list_custom_domains = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import list_custom_domains

            result = await list_custom_domains(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetCustomDomain:
    """Tests for get_custom_domain function."""

    @pytest.mark.asyncio
    async def test_get_custom_domain_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a specific custom domain."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import get_custom_domain

            result = await get_custom_domain(ctx=mock_context, domain_id="cd1abc123")
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "cd1abc123"

    @pytest.mark.asyncio
    async def test_get_custom_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import get_custom_domain

            result = await get_custom_domain(ctx=mock_context, domain_id="invalid")
            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_custom_domain_error(self, mock_context):
        """Test error handling when retrieving a custom domain fails."""
        mock_client = AsyncMock()
        mock_client.get_custom_domain = AsyncMock(return_value=(None, None, "Domain not found"))

        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import get_custom_domain

            result = await get_custom_domain(ctx=mock_context, domain_id="cd1abc123")
            assert result.get("success") is False
            assert "error" in result


class TestCreateCustomDomain:
    """Tests for create_custom_domain function."""

    @pytest.mark.asyncio
    async def test_create_custom_domain_success(self, mock_context, mock_okta_client):
        """Test successfully creating a custom domain."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import create_custom_domain

            result = await create_custom_domain(
                ctx=mock_context,
                domain="login.example.com",
                certificate_source_type="OKTA_MANAGED",
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_create_custom_domain_invalid_certificate_source_type(self, mock_context):
        """Test error handling with invalid certificate_source_type."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import create_custom_domain

            result = await create_custom_domain(
                ctx=mock_context,
                domain="login.example.com",
                certificate_source_type="INVALID",
            )
            assert result.get("success") is False
            assert "error" in result
            assert "OKTA_MANAGED" in result.get("error")

    @pytest.mark.asyncio
    async def test_create_custom_domain_error(self, mock_context):
        """Test error handling when creating a custom domain fails."""
        mock_client = AsyncMock()
        mock_client.create_custom_domain = AsyncMock(return_value=(None, None, "Creation failed"))

        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import create_custom_domain

            result = await create_custom_domain(
                ctx=mock_context,
                domain="login.example.com",
                certificate_source_type="OKTA_MANAGED",
            )
            assert result.get("success") is False
            assert "error" in result


class TestDeleteCustomDomain:
    """Tests for delete_custom_domain function."""

    def test_delete_custom_domain_returns_confirmation(self, mock_context):
        """Test that delete_custom_domain returns confirmation_required."""
        from okta_mcp_server.tools.custom_domains.custom_domains import delete_custom_domain

        result = delete_custom_domain(ctx=mock_context, domain_id="cd1abc123")
        assert result.get("success") is True
        assert result.get("confirmation_required") is True
        assert "DELETE" in result.get("message")

    def test_delete_custom_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        from okta_mcp_server.tools.custom_domains.custom_domains import delete_custom_domain

        result = delete_custom_domain(ctx=mock_context, domain_id="")
        assert result.get("success") is False
        assert "error" in result


class TestConfirmDeleteCustomDomain:
    """Tests for confirm_delete_custom_domain function."""

    @pytest.mark.asyncio
    async def test_confirm_delete_custom_domain_success(self, mock_context, mock_okta_client):
        """Test successfully confirming and deleting a custom domain."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import confirm_delete_custom_domain

            result = await confirm_delete_custom_domain(
                ctx=mock_context,
                domain_id="cd1abc123",
                confirmation="DELETE",
            )
            assert result.get("success") is True
            assert "message" in result.get("data")

    @pytest.mark.asyncio
    async def test_confirm_delete_custom_domain_wrong_confirmation(self, mock_context):
        """Test error handling with wrong confirmation code."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import confirm_delete_custom_domain

            result = await confirm_delete_custom_domain(
                ctx=mock_context,
                domain_id="cd1abc123",
                confirmation="WRONG",
            )
            assert result.get("success") is False
            assert "error" in result
            assert "DELETE" in result.get("error")

    @pytest.mark.asyncio
    async def test_confirm_delete_custom_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import confirm_delete_custom_domain

            result = await confirm_delete_custom_domain(
                ctx=mock_context,
                domain_id="invalid",
                confirmation="DELETE",
            )
            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_confirm_delete_custom_domain_error(self, mock_context):
        """Test error handling when API call fails."""
        mock_client = AsyncMock()
        mock_client.delete_custom_domain = AsyncMock(return_value=(None, "Deletion failed"))

        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import confirm_delete_custom_domain

            result = await confirm_delete_custom_domain(
                ctx=mock_context,
                domain_id="cd1abc123",
                confirmation="DELETE",
            )
            assert result.get("success") is False
            assert "error" in result


class TestVerifyCustomDomain:
    """Tests for verify_custom_domain function."""

    @pytest.mark.asyncio
    async def test_verify_custom_domain_success(self, mock_context, mock_okta_client):
        """Test successfully verifying a custom domain."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import verify_custom_domain

            result = await verify_custom_domain(ctx=mock_context, domain_id="cd1abc123")
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "cd1abc123"

    @pytest.mark.asyncio
    async def test_verify_custom_domain_invalid_id(self, mock_context):
        """Test error handling with invalid domain ID."""
        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import verify_custom_domain

            result = await verify_custom_domain(ctx=mock_context, domain_id="invalid")
            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_verify_custom_domain_error(self, mock_context):
        """Test error handling when verifying a custom domain fails."""
        mock_client = AsyncMock()
        mock_client.verify_custom_domain = AsyncMock(return_value=(None, None, "Verification failed"))

        with patch(
            "okta_mcp_server.tools.custom_domains.custom_domains.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.custom_domains.custom_domains import verify_custom_domain

            result = await verify_custom_domain(ctx=mock_context, domain_id="cd1abc123")
            assert result.get("success") is False
            assert "error" in result
