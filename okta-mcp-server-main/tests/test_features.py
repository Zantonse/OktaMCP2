# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for the Okta features management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListFeatures:
    """Tests for list_features function."""

    @pytest.mark.asyncio
    async def test_list_features_success(self, mock_context, mock_okta_client):
        """Test successfully listing features."""
        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.features.features import list_features

            result = await list_features(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_features_error(self, mock_context):
        """Test error handling when listing features fails."""
        mock_client = AsyncMock()
        mock_client.list_features = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.features.features import list_features

            result = await list_features(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetFeature:
    """Tests for get_feature function."""

    @pytest.mark.asyncio
    async def test_get_feature_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a specific feature."""
        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.features.features import get_feature

            result = await get_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "ftx123abc"

    @pytest.mark.asyncio
    async def test_get_feature_invalid_id(self, mock_context):
        """Test error handling for invalid feature ID."""
        from okta_mcp_server.tools.features.features import get_feature

        result = await get_feature(feature_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_feature_error(self, mock_context):
        """Test error handling when retrieving a feature fails."""
        mock_client = AsyncMock()
        mock_client.get_feature = AsyncMock(return_value=(None, None, "Feature not found"))

        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.features.features import get_feature

            result = await get_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestEnableFeature:
    """Tests for enable_feature function."""

    @pytest.mark.asyncio
    async def test_enable_feature_success(self, mock_context, mock_okta_client):
        """Test successfully enabling a feature."""
        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.features.features import enable_feature

            result = await enable_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").status == "ENABLED"

    @pytest.mark.asyncio
    async def test_enable_feature_with_mode(self, mock_context, mock_okta_client):
        """Test enabling a feature with mode parameter."""
        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.features.features import enable_feature

            result = await enable_feature(feature_id="ftx123abc", ctx=mock_context, mode="FORCE")
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").status == "ENABLED"

    @pytest.mark.asyncio
    async def test_enable_feature_invalid_id(self, mock_context):
        """Test error handling for invalid feature ID when enabling."""
        from okta_mcp_server.tools.features.features import enable_feature

        result = await enable_feature(feature_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_enable_feature_error(self, mock_context):
        """Test error handling when enabling a feature fails."""
        mock_client = AsyncMock()
        mock_client.update_feature_lifecycle = AsyncMock(return_value=(None, None, "API Error"))

        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.features.features import enable_feature

            result = await enable_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestDisableFeature:
    """Tests for disable_feature function."""

    @pytest.mark.asyncio
    async def test_disable_feature_success(self, mock_context, mock_okta_client):
        """Test successfully disabling a feature."""
        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.features.features import disable_feature

            result = await disable_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").status == "DISABLED"

    @pytest.mark.asyncio
    async def test_disable_feature_invalid_id(self, mock_context):
        """Test error handling for invalid feature ID when disabling."""
        from okta_mcp_server.tools.features.features import disable_feature

        result = await disable_feature(feature_id="invalid@#$%", ctx=mock_context)
        assert result.get("success") is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_disable_feature_error(self, mock_context):
        """Test error handling when disabling a feature fails."""
        mock_client = AsyncMock()
        mock_client.update_feature_lifecycle = AsyncMock(return_value=(None, None, "API Error"))

        with patch(
            "okta_mcp_server.tools.features.features.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.features.features import disable_feature

            result = await disable_feature(feature_id="ftx123abc", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result
