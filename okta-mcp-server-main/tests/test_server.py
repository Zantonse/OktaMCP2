# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for server lifecycle and initialization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from okta_mcp_server.server import OktaAppContext, okta_authorisation_flow


class TestOktaAppContext:
    """Tests for OktaAppContext dataclass."""

    def test_holds_auth_manager(self):
        mock_manager = MagicMock()
        ctx = OktaAppContext(okta_auth_manager=mock_manager)
        assert ctx.okta_auth_manager is mock_manager


class TestOktaAuthorisationFlow:
    """Tests for the lifespan context manager."""

    @pytest.mark.asyncio
    async def test_yields_context_with_manager(self):
        """Lifespan should authenticate and yield OktaAppContext."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            async with okta_authorisation_flow(mock_server) as ctx:
                assert isinstance(ctx, OktaAppContext)
                assert ctx.okta_auth_manager is mock_manager
                mock_manager.authenticate.assert_called_once()

    @pytest.mark.asyncio
    async def test_clears_tokens_on_exit(self):
        """Lifespan should clear tokens when context exits normally."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            async with okta_authorisation_flow(mock_server) as ctx:
                pass
            mock_manager.clear_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_clears_tokens_on_exception(self):
        """Lifespan should clear tokens even if an exception occurs."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock()
        mock_manager.clear_tokens = MagicMock()

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            with pytest.raises(RuntimeError):
                async with okta_authorisation_flow(mock_server) as ctx:
                    raise RuntimeError("tool failure")
            mock_manager.clear_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_propagates_auth_failure(self):
        """Lifespan should propagate authentication failures."""
        mock_manager = MagicMock()
        mock_manager.authenticate = AsyncMock(side_effect=RuntimeError("Auth failed"))

        with patch("okta_mcp_server.server.OktaAuthManager", return_value=mock_manager):
            mock_server = MagicMock()
            with pytest.raises(RuntimeError, match="Auth failed"):
                async with okta_authorisation_flow(mock_server) as ctx:
                    pass
