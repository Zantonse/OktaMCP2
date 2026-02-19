# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Shared pytest fixtures and mocks for Okta MCP Server tests."""

from dataclasses import dataclass
from typing import Dict, Optional
from unittest.mock import AsyncMock, patch

import pytest


@dataclass
class MockTempPassword:
    """Mock temporary password response."""

    temp_password: str = "TempPass123!"


@dataclass
class MockResetToken:
    """Mock password reset token response."""

    reset_password_url: str = "https://test.okta.com/reset/token"


@dataclass
class MockUserProfile:
    """Mock Okta user profile."""

    login: str = "test@example.com"
    email: str = "test@example.com"
    firstName: str = "Test"
    lastName: str = "User"
    displayName: str = "Test User"


@dataclass
class MockUser:
    """Mock Okta user object."""

    id: str = "00u1abc123def456"
    status: str = "ACTIVE"
    profile: MockUserProfile = None

    def __post_init__(self):
        if self.profile is None:
            self.profile = MockUserProfile()


@dataclass
class MockGroupProfile:
    """Mock Okta group profile."""

    name: str = "Test Group"
    description: str = "A test group"


@dataclass
class MockGroup:
    """Mock Okta group object."""

    id: str = "00g1abc123def456"
    profile: MockGroupProfile = None

    def __post_init__(self):
        if self.profile is None:
            self.profile = MockGroupProfile()


@dataclass
class MockAuthorizationServer:
    """Mock Okta authorization server object."""

    id: str = "aus1abc123"
    name: str = "Test Auth Server"
    description: str = "Test Description"
    status: str = "ACTIVE"
    audiences: list = None

    def __post_init__(self):
        if self.audiences is None:
            self.audiences = ["api://default"]


@dataclass
class MockPolicy:
    """Mock Okta policy object."""

    id: str = "00p1abc123"
    name: str = "Default Policy"
    status: str = "ACTIVE"

    def as_dict(self):
        return {"id": self.id, "name": self.name, "status": self.status}


@dataclass
class MockScope:
    """Mock OAuth2 scope object."""

    id: str = "scp1abc123"
    name: str = "test_scope"


@dataclass
class MockClaim:
    """Mock OAuth2 claim object."""

    id: str = "clm1abc123"
    name: str = "test_claim"


@dataclass
class MockIdentityProvider:
    """Mock Okta identity provider object."""

    id: str = "0oa1abc123"
    name: str = "Test IdP"
    type: str = "SAML2"
    status: str = "ACTIVE"


@dataclass
class MockFactor:
    """Mock Okta factor object."""

    id: str = "fct1abc123"
    factor_type: str = "sms"
    provider: str = "OKTA"
    status: str = "ACTIVE"


@dataclass
class MockNetworkZone:
    """Mock Okta network zone object."""

    id: str = "nzn1abc123"
    name: str = "Test Zone"
    type: str = "IP"
    status: str = "ACTIVE"
    gateways: list = None

    def __post_init__(self):
        if self.gateways is None:
            self.gateways = [{"type": "CIDR", "value": "10.0.0.0/8"}]


@dataclass
class MockTrustedOrigin:
    """Mock Okta trusted origin object."""

    id: str = "tos1abc123"
    name: str = "Test Origin"
    origin: str = "https://example.com"
    status: str = "ACTIVE"
    scopes: list = None

    def __post_init__(self):
        if self.scopes is None:
            self.scopes = [{"type": "CORS"}, {"type": "REDIRECT"}]


@dataclass
class MockRole:
    """Mock Okta role object."""

    id: str = "rol1abc123"
    type: str = "USER_ADMIN"
    status: str = "ACTIVE"
    label: str = "User Administrator"


@dataclass
class MockUserSchema:
    """Mock Okta user schema object."""

    id: str = "https://test.okta.com/meta/schemas/user/default"
    name: str = "user"
    definitions: dict = None

    def __post_init__(self):
        if self.definitions is None:
            self.definitions = {"base": {}, "custom": {}}


@dataclass
class MockUserType:
    """Mock Okta user type object."""

    id: str = "oty1abc123"
    name: str = "Default"
    display_name: str = "Default User Type"


@dataclass
class MockAppUserSchema:
    """Mock Okta app user schema object."""

    id: str = "https://test.okta.com/meta/schemas/apps/0oa123/default"
    name: str = "app_user"


@dataclass
class MockRoleTarget:
    """Mock Okta role target object."""

    id: str = "00g1abc123"
    type: str = "GROUP"


@dataclass
class MockBrand:
    """Mock Okta brand object."""

    id: str = "bnd1abc123"
    name: str = "Test Brand"


@dataclass
class MockBrandTheme:
    """Mock Okta brand theme object."""

    id: str = "thm1abc123"
    primary_color_hex: str = "#1662dd"
    secondary_color_hex: str = "#ffffff"


@dataclass
class MockAuthenticator:
    """Mock Okta authenticator object."""

    id: str = "aut1abc123"
    key: str = "okta_verify"
    name: str = "Okta Verify"
    type: str = "app"
    status: str = "ACTIVE"


@dataclass
class MockAuthenticatorMethod:
    """Mock Okta authenticator method object."""

    type: str = "push"
    status: str = "ACTIVE"


@dataclass
class MockBehaviorRule:
    """Mock Okta behavior detection rule object."""

    id: str = "bhv1abc123"
    name: str = "Test Behavior Rule"
    type: str = "ANOMALY_VELOCITY"
    status: str = "ACTIVE"
    settings: dict = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {"maxEventsUsedForEvaluation": 50}


@dataclass
class MockEmailTemplate:
    """Mock Okta email template object."""

    name: str = "UserActivation"
    subject: str = "Welcome to {{org.name}}"


@dataclass
class MockSignInPage:
    """Mock Okta sign-in page object."""

    widget_version: str = "^5"


@dataclass
class MockSession:
    """Mock Okta session object."""

    id: str = "ses1abc123def456"
    userId: str = "00u1abc123def456"
    createdAt: str = "2024-01-01T00:00:00.000Z"
    expiresAt: str = "2024-01-01T01:00:00.000Z"
    lastPasswordVerification: str = "2024-01-01T00:00:00.000Z"
    lastFactorVerification: str = "2024-01-01T00:00:00.000Z"
    amr: list = None
    idp: dict = None
    mfaActive: bool = False

    def __post_init__(self):
        if self.amr is None:
            self.amr = ["pwd"]
        if self.idp is None:
            self.idp = {"id": "00o1abc123", "type": "OKTA"}


@dataclass
class MockEventHook:
    """Mock Okta event hook object."""

    id: str = "who1abc123"
    name: str = "Test Event Hook"
    status: str = "ACTIVE"
    events: dict = None
    channel: dict = None

    def __post_init__(self):
        if self.events is None:
            self.events = {"type": "EVENT_TYPE", "items": ["user.lifecycle.create"]}
        if self.channel is None:
            self.channel = {"type": "HTTP", "version": "1.0.0", "config": {"uri": "https://example.com/hook"}}


@dataclass
class MockInlineHook:
    """Mock Okta inline hook object."""

    id: str = "inh1abc123"
    name: str = "Test Inline Hook"
    type: str = "com.okta.oauth2.tokens.transform"
    version: str = "1.0.0"
    status: str = "ACTIVE"
    channel: dict = None

    def __post_init__(self):
        if self.channel is None:
            self.channel = {"type": "HTTP", "version": "1.0.0", "config": {"uri": "https://example.com/hook"}}


@dataclass
class MockDevice:
    """Mock Okta device object."""

    id: str = "guo1abc123"
    status: str = "ACTIVE"
    display_name: str = "Test Device"
    platform: str = "MACOS"
    manufacturer: str = "Apple"
    model: str = "MacBook Pro"


@dataclass
class MockDeviceAssurancePolicy:
    """Mock Okta device assurance policy object."""

    id: str = "dap1abc123"
    name: str = "Test Device Assurance Policy"
    platform: str = "MACOS"
    disk_encryption_type: dict = None
    os_version: dict = None
    screen_lock_type: dict = None

    def __post_init__(self):
        if self.disk_encryption_type is None:
            self.disk_encryption_type = {"include": ["ALL_INTERNAL_VOLUMES"]}
        if self.os_version is None:
            self.os_version = {"minimum": "12.0"}
        if self.screen_lock_type is None:
            self.screen_lock_type = {"include": ["BIOMETRIC"]}


@dataclass
class MockFeature:
    """Mock Okta feature object."""

    id: str = "ftx1abc123"
    name: str = "Test Feature"
    description: str = "A test feature flag"
    status: str = "ENABLED"
    stage: dict = None
    type: str = "self-service"

    def __post_init__(self):
        if self.stage is None:
            self.stage = {"value": "EA", "state": "OPEN"}


@dataclass
class MockProfileMapping:
    """Mock Okta profile mapping object."""

    id: str = "prm1abc123"
    source: dict = None
    target: dict = None
    properties: dict = None

    def __post_init__(self):
        if self.source is None:
            self.source = {"id": "0oa1abc123", "type": "APP"}
        if self.target is None:
            self.target = {"id": "oty1abc123", "type": "USER"}
        if self.properties is None:
            self.properties = {"firstName": {"expression": "appuser.firstName"}}


@dataclass
class MockThreatInsightConfiguration:
    """Mock Okta ThreatInsight configuration object."""

    action: str = "audit"
    exclude_zones: list = None
    created: str = "2024-01-01T00:00:00.000Z"
    last_updated: str = "2024-01-01T00:00:00.000Z"
    _links: dict = None

    def __post_init__(self):
        if self.exclude_zones is None:
            self.exclude_zones = []
        if self._links is None:
            self._links = {}


@dataclass
class MockOrgSettings:
    """Mock Okta organization settings object."""

    id: str = "org1abc123"
    company_name: str = "Test Org"
    website: str = "https://test.example.com"
    phone_number: str = "+1-555-0100"
    address: dict = None

    def __post_init__(self):
        if self.address is None:
            self.address = {"streetAddress": "123 Test St", "city": "San Francisco", "state": "CA"}


@dataclass
class MockOrgContactUser:
    """Mock Okta organization contact user object."""

    user_id: str = "00u1abc123"
    contact_type: str = "TECHNICAL"


class MockOktaResponse:
    """Mock Okta API response object."""

    def __init__(self, has_next: bool = False, next_url: Optional[str] = None, next_page_data=None):
        self._has_next = has_next
        self._next = next_url
        self._next_page_data = next_page_data
        self._next_called = False

    def has_next(self) -> bool:
        if self._next_called:
            return False
        return self._has_next

    async def next(self):
        self._next_called = True
        if self._next_page_data:
            items, next_response = self._next_page_data
            self._has_next = next_response._has_next if next_response else False
            self._next = next_response._next if next_response else None
            self._next_page_data = next_response._next_page_data if next_response else None
            self._next_called = False
            return items, None
        return [], None


class MockOktaClient:
    """Mock Okta client for testing."""

    def __init__(self):
        self.users = [MockUser()]
        self.groups = [MockGroup()]

    async def list_users(self, query_params: Optional[Dict] = None):
        return self.users, MockOktaResponse(), None

    async def get_user(self, user_id: str):
        return MockUser(id=user_id)

    async def create_user(self, user_data: Dict):
        user = MockUser()
        if "profile" in user_data:
            user.profile = MockUserProfile(**user_data["profile"])
        return user, MockOktaResponse(), None

    async def update_user(self, user_id: str, user_data: Dict):
        user = MockUser(id=user_id)
        if "profile" in user_data:
            for key, value in user_data["profile"].items():
                setattr(user.profile, key, value)
        return user, MockOktaResponse(), None

    async def deactivate_user(self, user_id: str):
        return None, None

    async def deactivate_or_delete_user(self, user_id: str):
        return None, None

    async def list_groups(self, query_params: Optional[Dict] = None):
        return self.groups, MockOktaResponse(), None

    async def get_group(self, group_id: str):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def create_group(self, group_data: Dict):
        group = MockGroup()
        if "profile" in group_data:
            group.profile = MockGroupProfile(**group_data["profile"])
        return group, MockOktaResponse(), None

    async def update_group(self, group_id: str, group_data: Dict):
        group = MockGroup(id=group_id)
        if "profile" in group_data:
            for key, value in group_data["profile"].items():
                setattr(group.profile, key, value)
        return group, MockOktaResponse(), None

    async def delete_group(self, group_id: str):
        return None, None

    async def list_group_users(self, group_id: str, query_params: Optional[Dict] = None):
        return self.users, MockOktaResponse(), None

    async def list_assigned_applications_for_group(self, group_id: str):
        return [], MockOktaResponse(), None

    async def add_user_to_group(self, group_id: str, user_id: str):
        return None, None

    async def remove_user_from_group(self, group_id: str, user_id: str):
        return None, None

    async def activate_user(self, user_id: str):
        return None, None

    async def reactivate_user(self, user_id: str):
        return None, None

    async def suspend_user(self, user_id: str):
        return None, None

    async def unsuspend_user(self, user_id: str):
        return None, None

    async def unlock_user(self, user_id: str):
        return None, None

    async def expire_password(self, user_id: str):
        return None, None

    async def expire_password_and_get_temporary_password(self, user_id: str):
        return MockTempPassword(), None, None

    async def reset_password(self, user_id: str, params: Optional[Dict] = None):
        return MockResetToken(), None, None

    async def list_user_groups(self, user_id: str, query_params: Optional[Dict] = None):
        return self.groups, MockOktaResponse(), None

    async def list_app_links(self, user_id: str):
        return [], MockOktaResponse(), None

    async def list_applications(self, query_params: Optional[Dict] = None):
        apps = [type("MockApp", (), {"id": "0oa1abc123", "name": "Test App", "label": "Test Application"})]
        return apps, MockOktaResponse(), None

    async def get_application(self, app_id: str, query_params: Optional[Dict] = None):
        app = type("MockApp", (), {"id": app_id, "name": "Test App", "label": "Test Application"})
        return app, MockOktaResponse(), None

    async def create_application(self, app_config: Dict, query_params: Optional[Dict] = None):
        app = type(
            "MockApp", (), {"id": "0oa1abc123", "name": app_config.get("name"), "label": app_config.get("label")}
        )
        return app, MockOktaResponse(), None

    async def update_application(self, app_id: str, app_config: Dict):
        app = type("MockApp", (), {"id": app_id, "name": app_config.get("name"), "label": app_config.get("label")})
        return app, MockOktaResponse(), None

    async def delete_application(self, app_id: str):
        return None, None

    async def activate_application(self, app_id: str):
        return None, None

    async def deactivate_application(self, app_id: str):
        return None, None

    async def list_application_users(self, app_id, query_params=None):
        return self.users, MockOktaResponse(), None

    async def get_application_user(self, app_id, user_id):
        return MockUser(id=user_id), MockOktaResponse(), None

    async def assign_user_to_application(self, app_id, body):
        return MockUser(id=body.get("id", "test")), MockOktaResponse(), None

    async def delete_application_user(self, app_id, user_id):
        return None, None

    async def list_application_group_assignments(self, app_id, query_params=None):
        return self.groups, MockOktaResponse(), None

    async def get_application_group_assignment(self, app_id, group_id):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def create_application_group_assignment(self, app_id, group_id, body):
        return MockGroup(id=group_id), MockOktaResponse(), None

    async def delete_application_group_assignment(self, app_id, group_id):
        return None, None

    async def list_authorization_servers(self, query_params=None):
        return [MockAuthorizationServer()], MockOktaResponse(), None

    async def get_authorization_server(self, auth_server_id):
        return MockAuthorizationServer(id=auth_server_id), MockOktaResponse(), None

    async def create_authorization_server(self, body):
        return MockAuthorizationServer(), MockOktaResponse(), None

    async def update_authorization_server(self, auth_server_id, body):
        return MockAuthorizationServer(id=auth_server_id), MockOktaResponse(), None

    async def delete_authorization_server(self, auth_server_id):
        return None, None

    async def activate_authorization_server(self, auth_server_id):
        return None, None

    async def deactivate_authorization_server(self, auth_server_id):
        return None, None

    async def list_authorization_server_policies(self, auth_server_id, query_params=None):
        return [MockPolicy()], MockOktaResponse(), None

    async def create_authorization_server_policy(self, auth_server_id, body):
        return MockPolicy(), MockOktaResponse(), None

    async def list_o_auth2_scopes(self, auth_server_id, query_params=None):
        return [MockScope()], MockOktaResponse(), None

    async def create_o_auth2_scope(self, auth_server_id, body):
        return MockScope(), MockOktaResponse(), None

    async def list_o_auth2_claims(self, auth_server_id, query_params=None):
        return [MockClaim()], MockOktaResponse(), None

    async def create_o_auth2_claim(self, auth_server_id, body):
        return MockClaim(), MockOktaResponse(), None

    async def list_identity_providers(self, query_params=None):
        return [MockIdentityProvider()], MockOktaResponse(), None

    async def get_identity_provider(self, idp_id):
        return MockIdentityProvider(id=idp_id), MockOktaResponse(), None

    async def create_identity_provider(self, body):
        return MockIdentityProvider(), MockOktaResponse(), None

    async def update_identity_provider(self, idp_id, body):
        return MockIdentityProvider(id=idp_id), MockOktaResponse(), None

    async def delete_identity_provider(self, idp_id):
        return None, None

    async def activate_identity_provider(self, idp_id):
        return None, None

    async def deactivate_identity_provider(self, idp_id):
        return None, None

    async def list_factors(self, user_id):
        return [MockFactor()], MockOktaResponse(), None

    async def get_factor(self, user_id, factor_id):
        return MockFactor(id=factor_id), MockOktaResponse(), None

    async def enroll_factor(self, user_id, body):
        return MockFactor(), MockOktaResponse(), None

    async def activate_factor(self, user_id, factor_id, body):
        return MockFactor(id=factor_id), MockOktaResponse(), None

    async def delete_factor(self, user_id, factor_id):
        return None, None

    async def verify_factor(self, user_id, factor_id, body):
        return {"factorResult": "SUCCESS"}, MockOktaResponse(), None

    async def list_network_zones(self, query_params=None):
        return [MockNetworkZone()], MockOktaResponse(), None

    async def get_network_zone(self, zone_id):
        return MockNetworkZone(id=zone_id), MockOktaResponse(), None

    async def create_network_zone(self, body):
        return MockNetworkZone(), MockOktaResponse(), None

    async def update_network_zone(self, zone_id, body):
        return MockNetworkZone(id=zone_id), MockOktaResponse(), None

    async def delete_network_zone(self, zone_id):
        return None, None

    async def activate_network_zone(self, zone_id):
        return None, None

    async def deactivate_network_zone(self, zone_id):
        return None, None

    async def list_trusted_origins(self, query_params=None):
        return [MockTrustedOrigin()], MockOktaResponse(), None

    async def get_trusted_origin(self, origin_id):
        return MockTrustedOrigin(id=origin_id), MockOktaResponse(), None

    async def create_trusted_origin(self, body):
        return MockTrustedOrigin(), MockOktaResponse(), None

    async def update_trusted_origin(self, origin_id, body):
        return MockTrustedOrigin(id=origin_id), MockOktaResponse(), None

    async def delete_trusted_origin(self, origin_id):
        return None, None

    async def activate_trusted_origin(self, origin_id):
        return None, None

    async def deactivate_trusted_origin(self, origin_id):
        return None, None

    async def list_assigned_roles_for_user(self, user_id):
        return [MockRole()], MockOktaResponse(), None

    async def list_assigned_roles_for_group(self, group_id):
        return [MockRole()], MockOktaResponse(), None

    async def assign_role_to_user(self, user_id, body):
        return MockRole(), MockOktaResponse(), None

    async def unassign_role_from_user(self, user_id, role_id):
        return None, None

    async def assign_role_to_group(self, group_id, body):
        return MockRole(), MockOktaResponse(), None

    async def unassign_role_from_group(self, group_id, role_id):
        return None, None

    async def list_group_targets_for_role(self, user_id, role_id):
        return [MockRoleTarget()], MockOktaResponse(), None

    async def list_application_targets_for_administrator_role_for_user(self, user_id, role_id):
        return [MockRoleTarget(type="APP")], MockOktaResponse(), None

    async def add_group_target_to_role(self, user_id, role_id, group_id):
        return None, None

    async def add_application_target_to_admin_role_for_user(self, user_id, role_id, app_id):
        return None, None

    async def remove_group_target_from_role(self, user_id, role_id, group_id):
        return None, None

    async def remove_application_target_from_administrator_role_for_user(self, user_id, role_id, app_id):
        return None, None

    async def get_user_schema(self, type_id):
        return MockUserSchema(), MockOktaResponse(), None

    async def list_user_types(self):
        return [MockUserType()], MockOktaResponse(), None

    async def update_user_profile(self, type_id, body):
        return MockUserSchema(), MockOktaResponse(), None

    async def get_application_user_schema(self, app_id):
        return MockAppUserSchema(), MockOktaResponse(), None

    async def update_application_user_profile(self, app_id, body):
        return MockAppUserSchema(), MockOktaResponse(), None

    async def list_brands(self):
        return [MockBrand()], MockOktaResponse(), None

    async def get_brand(self, brand_id):
        return MockBrand(id=brand_id), MockOktaResponse(), None

    async def update_brand(self, brand_id, body):
        return MockBrand(id=brand_id), MockOktaResponse(), None

    async def list_brand_themes(self, brand_id):
        return [MockBrandTheme()], MockOktaResponse(), None

    async def get_brand_theme(self, brand_id, theme_id):
        return MockBrandTheme(id=theme_id), MockOktaResponse(), None

    async def update_brand_theme(self, brand_id, theme_id, body):
        return MockBrandTheme(id=theme_id), MockOktaResponse(), None

    async def upload_brand_theme_logo(self, brand_id, theme_id, file):
        return {"url": "https://example.com/logo.png"}, MockOktaResponse(), None

    async def upload_brand_theme_favicon(self, brand_id, theme_id, file):
        return {"url": "https://example.com/favicon.ico"}, MockOktaResponse(), None

    async def get_email_template(self, brand_id, template_name):
        return MockEmailTemplate(name=template_name), MockOktaResponse(), None

    async def update_email_template(self, brand_id, template_name, body):
        return MockEmailTemplate(name=template_name), MockOktaResponse(), None

    async def get_sign_in_page(self, brand_id):
        return MockSignInPage(), MockOktaResponse(), None

    async def update_sign_in_page(self, brand_id, body):
        return MockSignInPage(), MockOktaResponse(), None

    async def list_authenticators(self):
        return [MockAuthenticator()], MockOktaResponse(), None

    async def get_authenticator(self, authenticator_id):
        return MockAuthenticator(id=authenticator_id), MockOktaResponse(), None

    async def activate_authenticator(self, authenticator_id):
        return MockAuthenticator(id=authenticator_id, status="ACTIVE"), None

    async def deactivate_authenticator(self, authenticator_id):
        return MockAuthenticator(id=authenticator_id, status="INACTIVE"), None

    async def list_authenticator_methods(self, authenticator_id):
        return [MockAuthenticatorMethod()], MockOktaResponse(), None

    async def get_authenticator_method(self, authenticator_id, method_type):
        return MockAuthenticatorMethod(type=method_type), MockOktaResponse(), None

    async def activate_authenticator_method(self, authenticator_id, method_type):
        return MockAuthenticatorMethod(type=method_type, status="ACTIVE"), None

    async def deactivate_authenticator_method(self, authenticator_id, method_type):
        return MockAuthenticatorMethod(type=method_type, status="INACTIVE"), None

    async def list_behavior_detection_rules(self):
        return [MockBehaviorRule()], MockOktaResponse(), None

    async def get_behavior_detection_rule(self, behavior_id):
        return MockBehaviorRule(id=behavior_id), MockOktaResponse(), None

    async def create_behavior_detection_rule(self, body):
        return MockBehaviorRule(), MockOktaResponse(), None

    async def update_behavior_detection_rule(self, behavior_id, body):
        return MockBehaviorRule(id=behavior_id), MockOktaResponse(), None

    async def delete_behavior_detection_rule(self, behavior_id):
        return None, None

    async def activate_behavior_detection_rule(self, behavior_id):
        return MockBehaviorRule(id=behavior_id, status="ACTIVE"), MockOktaResponse(), None

    async def deactivate_behavior_detection_rule(self, behavior_id):
        return MockBehaviorRule(id=behavior_id, status="INACTIVE"), MockOktaResponse(), None

    async def list_policies(self, params):
        return [MockPolicy()], MockOktaResponse(), None

    async def get_policy(self, policy_id):
        return MockPolicy(id=policy_id), MockOktaResponse(), None

    async def create_policy(self, policy_data):
        policy = MockPolicy()
        if "name" in policy_data:
            policy.name = policy_data["name"]
        return policy, MockOktaResponse(), None

    async def update_policy(self, policy_id, policy_data):
        policy = MockPolicy(id=policy_id)
        if "name" in policy_data:
            policy.name = policy_data["name"]
        return policy, MockOktaResponse(), None

    async def delete_policy(self, policy_id):
        return None, None

    async def activate_policy(self, policy_id):
        return None, None

    async def deactivate_policy(self, policy_id):
        return None, None

    async def list_policy_rules(self, policy_id):
        rule = type(
            "MockPolicyRule",
            (),
            {"id": "rule1", "name": "Test Rule", "as_dict": lambda self: {"id": self.id, "name": self.name}},
        )()
        return [rule], MockOktaResponse(), None

    async def get_policy_rule(self, policy_id, rule_id):
        rule = type(
            "MockPolicyRule",
            (),
            {"id": rule_id, "name": "Test Rule", "as_dict": lambda self: {"id": self.id, "name": self.name}},
        )()
        return rule, MockOktaResponse(), None

    async def create_policy_rule(self, policy_id, rule_data):
        rule = type(
            "MockPolicyRule",
            (),
            {
                "id": "rule1",
                "name": rule_data.get("name", "Test Rule"),
                "as_dict": lambda self: {"id": self.id, "name": self.name},
            },
        )()
        return rule, MockOktaResponse(), None

    async def update_policy_rule(self, policy_id, rule_id, rule_data):
        rule = type(
            "MockPolicyRule",
            (),
            {
                "id": rule_id,
                "name": rule_data.get("name", "Test Rule"),
                "as_dict": lambda self: {"id": self.id, "name": self.name},
            },
        )()
        return rule, MockOktaResponse(), None

    async def delete_policy_rule(self, policy_id, rule_id):
        return None, None

    async def activate_policy_rule(self, policy_id, rule_id):
        return None, None

    async def deactivate_policy_rule(self, policy_id, rule_id):
        return None, None

    async def get_logs(self, query_params):
        logs = [
            type(
                "MockLog",
                (),
                {
                    "id": f"log_{i}",
                    "eventType": "user.lifecycle.create",
                    "published": "2024-01-01T00:00:00.000Z",
                    "actor": {"id": "actor1", "displayName": "Admin User", "type": "User"},
                    "client": {"ipAddress": "192.168.1.1"},
                    "outcome": {"result": "SUCCESS"},
                    "as_dict": lambda: {"id": f"log_{i}", "eventType": "user.lifecycle.create"},
                },
            )()
            for i in range(3)
        ]
        return logs, MockOktaResponse(), None

    async def get_session(self, session_id):
        return MockSession(id=session_id), MockOktaResponse(), None

    async def create_session(self, body):
        return MockSession(), MockOktaResponse(), None

    async def refresh_session(self, session_id):
        return MockSession(id=session_id), MockOktaResponse(), None

    async def close_session(self, session_id):
        return None, None

    async def revoke_user_sessions(self, user_id):
        return None, None

    async def list_event_hooks(self):
        return [MockEventHook()], MockOktaResponse(), None

    async def get_event_hook(self, event_hook_id):
        return MockEventHook(id=event_hook_id), MockOktaResponse(), None

    async def create_event_hook(self, body):
        return MockEventHook(), MockOktaResponse(), None

    async def update_event_hook(self, event_hook_id, body):
        return MockEventHook(id=event_hook_id), MockOktaResponse(), None

    async def delete_event_hook(self, event_hook_id):
        return None, None

    async def activate_event_hook(self, event_hook_id):
        return MockEventHook(id=event_hook_id, status="ACTIVE"), MockOktaResponse(), None

    async def deactivate_event_hook(self, event_hook_id):
        return MockEventHook(id=event_hook_id, status="INACTIVE"), MockOktaResponse(), None

    async def verify_event_hook(self, event_hook_id):
        return MockEventHook(id=event_hook_id, status="VERIFIED"), MockOktaResponse(), None

    async def list_inline_hooks(self, query_params=None):
        return [MockInlineHook()], MockOktaResponse(), None

    async def get_inline_hook(self, inline_hook_id):
        return MockInlineHook(id=inline_hook_id), MockOktaResponse(), None

    async def create_inline_hook(self, body):
        return MockInlineHook(), MockOktaResponse(), None

    async def update_inline_hook(self, inline_hook_id, body):
        return MockInlineHook(id=inline_hook_id), MockOktaResponse(), None

    async def delete_inline_hook(self, inline_hook_id):
        return None, None

    async def activate_inline_hook(self, inline_hook_id):
        return MockInlineHook(id=inline_hook_id, status="ACTIVE"), MockOktaResponse(), None

    async def deactivate_inline_hook(self, inline_hook_id):
        return MockInlineHook(id=inline_hook_id, status="INACTIVE"), MockOktaResponse(), None

    async def execute_inline_hook(self, inline_hook_id, body):
        return {"status": "SUCCESS"}, MockOktaResponse(), None

    async def list_devices(self):
        return [MockDevice()], MockOktaResponse(), None

    async def get_device(self, device_id):
        return MockDevice(id=device_id), MockOktaResponse(), None

    async def delete_device(self, device_id):
        return None, None

    async def list_user_devices(self, user_id):
        return [MockDevice()], MockOktaResponse(), None

    async def list_device_assurance_policies(self):
        return [MockDeviceAssurancePolicy()], MockOktaResponse(), None

    async def get_device_assurance_policy(self, policy_id):
        return MockDeviceAssurancePolicy(id=policy_id), MockOktaResponse(), None

    async def create_device_assurance_policy(self, body):
        return MockDeviceAssurancePolicy(), MockOktaResponse(), None

    async def replace_device_assurance_policy(self, policy_id, body):
        return MockDeviceAssurancePolicy(id=policy_id), MockOktaResponse(), None

    async def delete_device_assurance_policy(self, policy_id):
        return None, None

    async def list_features(self):
        return [MockFeature()], MockOktaResponse(), None

    async def get_feature(self, feature_id):
        return MockFeature(id=feature_id), MockOktaResponse(), None

    async def update_feature_lifecycle(self, feature_id, lifecycle, mode=None):
        status = "ENABLED" if lifecycle == "enable" else "DISABLED"
        return MockFeature(id=feature_id, status=status), MockOktaResponse(), None

    async def list_profile_mappings(self, query_params=None):
        return [MockProfileMapping()], MockOktaResponse(), None

    async def get_profile_mapping(self, mapping_id):
        return MockProfileMapping(id=mapping_id), MockOktaResponse(), None

    async def update_profile_mapping(self, mapping_id, body):
        return MockProfileMapping(id=mapping_id), MockOktaResponse(), None

    async def get_current_configuration(self):
        return MockThreatInsightConfiguration(), MockOktaResponse(), None

    async def update_configuration(self, body):
        config = MockThreatInsightConfiguration()
        if "action" in body:
            config.action = body["action"]
        if "excludeZones" in body:
            config.exclude_zones = body["excludeZones"]
        return config, MockOktaResponse(), None

    async def get_org_settings(self):
        return MockOrgSettings(), MockOktaResponse(), None

    async def partial_update_org_setting(self, body):
        settings = MockOrgSettings()
        if "companyName" in body:
            settings.company_name = body["companyName"]
        if "website" in body:
            settings.website = body["website"]
        if "phoneNumber" in body:
            settings.phone_number = body["phoneNumber"]
        if "address" in body:
            settings.address = body["address"]
        return settings, MockOktaResponse(), None

    async def get_org_contact_types(self):
        return [{"contactType": "TECHNICAL"}, {"contactType": "BILLING"}], MockOktaResponse(), None

    async def get_org_contact_user(self, contact_type):
        return MockOrgContactUser(contact_type=contact_type), MockOktaResponse(), None


class MockOktaAuthManager:
    """Mock OktaAuthManager for testing."""

    def __init__(self):
        self.org_url = "https://test.okta.com"
        self.client_id = "test_client_id"
        self.token_timestamp = 0
        self.use_browserless_auth = False

    async def authenticate(self):
        pass

    async def is_valid_token(self, expiry_duration: int = 3600) -> bool:
        return True

    async def refresh_access_token(self) -> bool:
        return True

    def clear_tokens(self):
        pass


class MockLifespanContext:
    """Mock lifespan context."""

    def __init__(self):
        self.okta_auth_manager = MockOktaAuthManager()


class MockRequestContext:
    """Mock request context."""

    def __init__(self):
        self.lifespan_context = MockLifespanContext()


class MockContext:
    """Mock MCP Context."""

    def __init__(self):
        self.request_context = MockRequestContext()


@pytest.fixture
def mock_context():
    """Provide a mock MCP context."""
    return MockContext()


@pytest.fixture
def mock_okta_client():
    """Provide a mock Okta client."""
    return MockOktaClient()


@pytest.fixture
def mock_auth_manager():
    """Provide a mock auth manager."""
    return MockOktaAuthManager()


@pytest.fixture
def mock_user():
    """Provide a mock user."""
    return MockUser()


@pytest.fixture
def mock_group():
    """Provide a mock group."""
    return MockGroup()


@pytest.fixture
def env_vars(monkeypatch):
    """Set required environment variables for testing."""
    monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
    monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")


@pytest.fixture
def mock_get_okta_client(mock_okta_client):
    """Patch get_okta_client to return mock client."""
    with patch(
        "okta_mcp_server.utils.client.get_okta_client",
        new_callable=AsyncMock,
        return_value=mock_okta_client,
    ) as mock:
        yield mock
