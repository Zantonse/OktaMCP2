# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Tests for policy management tools."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListPolicies:
    """Tests for list_policies tool."""

    @pytest.mark.asyncio
    async def test_list_policies_success(self, mock_context, mock_okta_client):
        """Test successful policies listing."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON")

            assert result.get("success") is True
            assert "policies" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_list_policies_with_status_filter(self, mock_context, mock_okta_client):
        """Test policies listing with status filter."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="PASSWORD", status="ACTIVE")

            assert result.get("success") is True
            assert "policies" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_list_policies_with_query(self, mock_context, mock_okta_client):
        """Test policies listing with search query."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="MFA_ENROLL", q="test")

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_list_policies_limit_validation(self, mock_context, mock_okta_client):
        """Test that limit parameter is validated."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policies

            # Test with limit below minimum
            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON", limit=5)
            assert result.get("success") is True

            # Test with limit above maximum
            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON", limit=200)
            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_list_policies_api_error(self, mock_context):
        """Test error handling for API failures."""
        mock_client = AsyncMock()
        mock_client.list_policies = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON")

            assert result.get("success") is False
            assert "error" in result


class TestGetPolicy:
    """Tests for get_policy tool."""

    @pytest.mark.asyncio
    async def test_get_policy_success(self, mock_context, mock_okta_client):
        """Test successful policy retrieval."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import get_policy

            result = await get_policy(ctx=mock_context, policy_id="00p1abc123")

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_get_policy_error(self, mock_context):
        """Test error handling for get policy."""
        mock_client = AsyncMock()
        mock_client.get_policy = AsyncMock(side_effect=Exception("Policy not found"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import get_policy

            result = await get_policy(ctx=mock_context, policy_id="invalid_id")

            assert result.get("success") is False
            assert "error" in result


class TestCreatePolicy:
    """Tests for create_policy tool."""

    @pytest.mark.asyncio
    async def test_create_policy_success(self, mock_context, mock_okta_client):
        """Test successful policy creation."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy

            policy_data = {
                "type": "OKTA_SIGN_ON",
                "name": "New Policy",
                "status": "ACTIVE",
            }
            result = await create_policy(ctx=mock_context, policy_data=policy_data)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_policy_with_description(self, mock_context, mock_okta_client):
        """Test policy creation with description."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy

            policy_data = {
                "type": "PASSWORD",
                "name": "Password Policy",
                "description": "Test password policy",
            }
            result = await create_policy(ctx=mock_context, policy_data=policy_data)

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_policy_api_error(self, mock_context):
        """Test error handling for policy creation."""
        mock_client = AsyncMock()
        mock_client.create_policy = AsyncMock(side_effect=Exception("Invalid policy data"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy

            policy_data = {"type": "INVALID_TYPE", "name": "Test"}
            result = await create_policy(ctx=mock_context, policy_data=policy_data)

            assert result.get("success") is False
            assert "error" in result


class TestDeletePolicy:
    """Tests for delete_policy tool."""

    @pytest.mark.asyncio
    async def test_delete_policy_success(self, mock_context, mock_okta_client):
        """Test successful policy deletion."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import delete_policy

            result = await delete_policy(ctx=mock_context, policy_id="00p1abc123")

            assert result.get("success") is True
            assert "message" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_delete_policy_error(self, mock_context):
        """Test error handling for policy deletion."""
        mock_client = AsyncMock()
        mock_client.delete_policy = AsyncMock(side_effect=Exception("Policy not found"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import delete_policy

            result = await delete_policy(ctx=mock_context, policy_id="invalid_id")

            assert result.get("success") is False
            assert "error" in result


class TestActivatePolicy:
    """Tests for activate_policy tool."""

    @pytest.mark.asyncio
    async def test_activate_policy_success(self, mock_context, mock_okta_client):
        """Test successful policy activation."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import activate_policy

            result = await activate_policy(ctx=mock_context, policy_id="00p1abc123")

            assert result.get("success") is True
            assert "message" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_activate_policy_error(self, mock_context):
        """Test error handling for policy activation."""
        mock_client = AsyncMock()
        mock_client.activate_policy = AsyncMock(side_effect=Exception("Cannot activate policy"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import activate_policy

            result = await activate_policy(ctx=mock_context, policy_id="invalid_id")

            assert result.get("success") is False
            assert "error" in result


class TestDeactivatePolicy:
    """Tests for deactivate_policy tool."""

    @pytest.mark.asyncio
    async def test_deactivate_policy_success(self, mock_context, mock_okta_client):
        """Test successful policy deactivation."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import deactivate_policy

            result = await deactivate_policy(ctx=mock_context, policy_id="00p1abc123")

            assert result.get("success") is True
            assert "message" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_deactivate_policy_error(self, mock_context):
        """Test error handling for policy deactivation."""
        mock_client = AsyncMock()
        mock_client.deactivate_policy = AsyncMock(side_effect=Exception("Cannot deactivate policy"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import deactivate_policy

            result = await deactivate_policy(ctx=mock_context, policy_id="invalid_id")

            assert result.get("success") is False
            assert "error" in result


class TestListPolicyRules:
    """Tests for list_policy_rules tool."""

    @pytest.mark.asyncio
    async def test_list_policy_rules_success(self, mock_context, mock_okta_client):
        """Test successful policy rules listing."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policy_rules

            result = await list_policy_rules(ctx=mock_context, policy_id="00p1abc123")

            assert result.get("success") is True
            assert "rules" in result.get("data", {})

    @pytest.mark.asyncio
    async def test_list_policy_rules_error(self, mock_context):
        """Test error handling for listing policy rules."""
        mock_client = AsyncMock()
        mock_client.list_policy_rules = AsyncMock(side_effect=Exception("Policy not found"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import list_policy_rules

            result = await list_policy_rules(ctx=mock_context, policy_id="invalid_id")

            assert result.get("success") is False
            assert "error" in result


class TestCreatePolicyRule:
    """Tests for create_policy_rule tool."""

    @pytest.mark.asyncio
    async def test_create_policy_rule_success(self, mock_context, mock_okta_client):
        """Test successful policy rule creation."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy_rule

            rule_data = {
                "name": "New Rule",
                "priority": 1,
            }
            result = await create_policy_rule(ctx=mock_context, policy_id="00p1abc123", rule_data=rule_data)

            assert result.get("success") is True
            assert result.get("data") is not None

    @pytest.mark.asyncio
    async def test_create_policy_rule_with_conditions(self, mock_context, mock_okta_client):
        """Test policy rule creation with conditions."""
        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy_rule

            rule_data = {
                "name": "Test Rule",
                "priority": 1,
                "conditions": {"userType": {"type": "USER_TYPE"}},
            }
            result = await create_policy_rule(ctx=mock_context, policy_id="00p1abc123", rule_data=rule_data)

            assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_policy_rule_api_error(self, mock_context):
        """Test error handling for policy rule creation."""
        mock_client = AsyncMock()
        mock_client.create_policy_rule = AsyncMock(side_effect=Exception("Invalid rule data"))

        with patch(
            "okta_mcp_server.tools.policies.policies.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.policies.policies import create_policy_rule

            rule_data = {"name": "Test"}
            result = await create_policy_rule(ctx=mock_context, policy_id="00p1abc123", rule_data=rule_data)

            assert result.get("success") is False
            assert "error" in result
