# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for the Okta factors management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListUserFactors:
    """Tests for list_user_factors function."""

    @pytest.mark.asyncio
    async def test_list_user_factors_success(self, mock_context, mock_okta_client):
        """Test successfully listing factors for a user."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import list_user_factors

            result = await list_user_factors(user_id="00u123", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_user_factors_error(self, mock_context):
        """Test error handling when listing factors fails."""
        mock_client = AsyncMock()
        mock_client.list_factors = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import list_user_factors

            result = await list_user_factors(user_id="00u123", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetUserFactor:
    """Tests for get_user_factor function."""

    @pytest.mark.asyncio
    async def test_get_user_factor_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a specific factor."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import get_user_factor

            result = await get_user_factor(user_id="00u123", factor_id="fct456", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "fct456"

    @pytest.mark.asyncio
    async def test_get_user_factor_error(self, mock_context):
        """Test error handling when retrieving a factor fails."""
        mock_client = AsyncMock()
        mock_client.get_factor = AsyncMock(return_value=(None, None, "Factor not found"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import get_user_factor

            result = await get_user_factor(user_id="00u123", factor_id="fct456", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestEnrollFactor:
    """Tests for enroll_factor function."""

    @pytest.mark.asyncio
    async def test_enroll_factor_success(self, mock_context, mock_okta_client):
        """Test successfully enrolling a new factor."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import enroll_factor

            result = await enroll_factor(
                user_id="00u123",
                factor_type="sms",
                ctx=mock_context,
                provider="OKTA",
                profile={"phoneNumber": "+1-555-123-4567"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").factor_type == "sms"

    @pytest.mark.asyncio
    async def test_enroll_factor_minimal(self, mock_context, mock_okta_client):
        """Test enrolling a factor with minimal parameters."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import enroll_factor

            result = await enroll_factor(
                user_id="00u123",
                factor_type="totp",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_enroll_factor_error(self, mock_context):
        """Test error handling when enrolling a factor fails."""
        mock_client = AsyncMock()
        mock_client.enroll_factor = AsyncMock(return_value=(None, None, "Invalid factor type"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import enroll_factor

            result = await enroll_factor(
                user_id="00u123",
                factor_type="invalid",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result


class TestActivateFactor:
    """Tests for activate_factor function."""

    @pytest.mark.asyncio
    async def test_activate_factor_success(self, mock_context, mock_okta_client):
        """Test successfully activating a factor."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import activate_factor

            result = await activate_factor(
                user_id="00u123",
                factor_id="fct456",
                ctx=mock_context,
                pass_code="123456",
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "fct456"

    @pytest.mark.asyncio
    async def test_activate_factor_without_passcode(self, mock_context, mock_okta_client):
        """Test activating a factor without a passcode."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import activate_factor

            result = await activate_factor(
                user_id="00u123",
                factor_id="fct456",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_activate_factor_error(self, mock_context):
        """Test error handling when activating a factor fails."""
        mock_client = AsyncMock()
        mock_client.activate_factor = AsyncMock(return_value=(None, None, "Invalid passcode"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import activate_factor

            result = await activate_factor(
                user_id="00u123",
                factor_id="fct456",
                pass_code="invalid",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result


class TestResetFactor:
    """Tests for reset_factor function."""

    @pytest.mark.asyncio
    async def test_reset_factor_success(self, mock_context, mock_okta_client):
        """Test successfully resetting a factor."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import reset_factor

            result = await reset_factor(user_id="00u123", factor_id="fct456", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert "message" in result.get("data")

    @pytest.mark.asyncio
    async def test_reset_factor_error(self, mock_context):
        """Test error handling when resetting a factor fails."""
        mock_client = AsyncMock()
        mock_client.delete_factor = AsyncMock(return_value=(None, "Factor not found"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import reset_factor

            result = await reset_factor(user_id="00u123", factor_id="fct456", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestVerifyFactor:
    """Tests for verify_factor function."""

    @pytest.mark.asyncio
    async def test_verify_factor_success(self, mock_context, mock_okta_client):
        """Test successfully verifying a factor."""
        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.factors.factors import verify_factor

            result = await verify_factor(
                user_id="00u123",
                factor_id="fct456",
                pass_code="123456",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").get("factorResult") == "SUCCESS"

    @pytest.mark.asyncio
    async def test_verify_factor_error(self, mock_context):
        """Test error handling when verifying a factor fails."""
        mock_client = AsyncMock()
        mock_client.verify_factor = AsyncMock(return_value=(None, None, "Verification failed"))

        with patch(
            "okta_mcp_server.tools.factors.factors.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.factors.factors import verify_factor

            result = await verify_factor(
                user_id="00u123",
                factor_id="fct456",
                pass_code="invalid",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result
