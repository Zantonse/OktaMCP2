# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for ThreatInsight configuration tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetThreatInsightConfiguration:
    """Tests for get_threat_insight_configuration tool."""

    @pytest.mark.asyncio
    async def test_get_threat_insight_configuration_success(self, mock_context, mock_okta_client):
        """Test successful retrieval of ThreatInsight configuration."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import get_threat_insight_configuration

            result = await get_threat_insight_configuration(ctx=mock_context)

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").action == "audit"
            assert result.get("data").exclude_zones == []

    @pytest.mark.asyncio
    async def test_get_threat_insight_configuration_api_error(self, mock_context):
        """Test error handling when Okta API returns error."""
        mock_client = AsyncMock()
        mock_client.get_current_configuration = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import get_threat_insight_configuration

            result = await get_threat_insight_configuration(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_threat_insight_configuration_okta_error_tuple(self, mock_context):
        """Test error handling when Okta SDK returns error in tuple."""
        mock_client = AsyncMock()
        mock_client.get_current_configuration = AsyncMock(return_value=(None, None, "Connection Error"))

        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import get_threat_insight_configuration

            result = await get_threat_insight_configuration(ctx=mock_context)

            assert result.get("success") is False
            assert "error" in result


class TestUpdateThreatInsightConfiguration:
    """Tests for update_threat_insight_configuration tool."""

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_success_block(self, mock_context, mock_okta_client):
        """Test successful update of ThreatInsight configuration with block action."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="block")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").action == "block"

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_success_audit(self, mock_context, mock_okta_client):
        """Test successful update of ThreatInsight configuration with audit action."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="audit")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").action == "audit"

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_success_none(self, mock_context, mock_okta_client):
        """Test successful update of ThreatInsight configuration with none action."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="none")

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").action == "none"

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_with_exclude_zones(self, mock_context, mock_okta_client):
        """Test successful update with exclude_zones parameter."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            exclude_zones = ["nzn1abc123", "nzn2def456"]
            result = await update_threat_insight_configuration(
                ctx=mock_context, action="block", exclude_zones=exclude_zones
            )

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").action == "block"
            assert result.get("data").exclude_zones == exclude_zones

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_invalid_action(self, mock_context):
        """Test update_threat_insight_configuration with invalid action."""
        from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

        result = await update_threat_insight_configuration(ctx=mock_context, action="invalid_action")

        assert result.get("success") is False
        assert "error" in result
        assert "Invalid action" in result.get("error")

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_api_error(self, mock_context):
        """Test error handling when Okta API returns error during update."""
        mock_client = AsyncMock()
        mock_client.update_configuration = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="block")

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_okta_error_tuple(self, mock_context):
        """Test error handling when Okta SDK returns error in tuple."""
        mock_client = AsyncMock()
        mock_client.update_configuration = AsyncMock(return_value=(None, None, "Invalid Request"))

        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="audit")

            assert result.get("success") is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_update_threat_insight_configuration_empty_exclude_zones(self, mock_context, mock_okta_client):
        """Test update with empty exclude_zones list."""
        with patch(
            "okta_mcp_server.tools.threat_insight.threat_insight.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.threat_insight.threat_insight import update_threat_insight_configuration

            result = await update_threat_insight_configuration(ctx=mock_context, action="block", exclude_zones=[])

            assert result.get("success") is True
            assert result.get("data") is not None
            assert result.get("data").exclude_zones == []
