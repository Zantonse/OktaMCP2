# Documentation Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Document all 19 tool modules (169 tools) by restructuring README.md and updating CLAUDE.md.

**Architecture:** In-place edits to two files. README gets a full "Supported Tools" section rewrite with an overview table and per-module tables grouped by category. CLAUDE.md gets 5 new rows in the tool table.

**Tech Stack:** Markdown only. No code changes.

---

### Task 1: Update CLAUDE.md Tool Table

**Files:**
- Modify: `CLAUDE.md:48-63` (the tool module table in Architecture section)

**Step 1: Add 5 new module rows to the table**

Insert these 5 rows into the existing table, maintaining alphabetical order. The table currently has 14 rows (applications through trusted_origins). Add these in their correct alphabetical positions:

After `authenticators` row, add:
```
| behaviors | `tools/behaviors/behaviors.py` | Behavior detection rule management |
```

After `brands` row, add:
```
| devices | `tools/devices/devices.py` | Device management |
| event_hooks | `tools/event_hooks/event_hooks.py` | Event hook management |
```

After `schemas` row, add:
```
| sessions | `tools/sessions/sessions.py` | Session management |
```

After `system_logs` row, add:
```
| threat_insight | `tools/threat_insight/threat_insight.py` | ThreatInsight configuration |
```

The final table should have 19 rows in alphabetical order.

**Step 2: Verify**

Read the file and confirm all 19 modules are present in the table.

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add Phase 1 tool modules to CLAUDE.md"
```

---

### Task 2: Rewrite README "Supported Tools" Section — Overview Table

**Files:**
- Modify: `README.md:221-287` (the entire "Supported Tools" section)

**Step 1: Replace the section header and add overview table**

Replace everything from line 221 (`## 🛠️ Supported Tools`) through line 287 (the last Logs table row) with the new content.

The new section starts with:

```markdown
## 🛠️ Supported Tools

The Okta MCP Server provides **169 tools across 19 domains** for LLMs to interact with your Okta tenant.

### Overview

| Category | Module | Tools | Description |
|----------|--------|-------|-------------|
| **Identity** | Users | 17 | User CRUD, lifecycle management, password operations |
| **Identity** | Groups | 10 | Group CRUD, membership management |
| **Identity** | Schemas | 8 | User profile schema and custom attributes |
| **Applications** | Applications | 16 | App CRUD, user/group assignment |
| **Applications** | Trusted Origins | 8 | CORS trusted origin management |
| **Security** | Policies | 14 | Policy and policy rule management |
| **Security** | Roles | 10 | Admin role assignment and targeting |
| **Security** | Authorization Servers | 14 | OAuth server, scopes, claims, policies |
| **Security** | Authenticators | 8 | Authenticator and method configuration |
| **Security** | Factors | 6 | MFA factor enrollment and verification |
| **Monitoring** | System Logs | 1 | System log retrieval with filtering |
| **Monitoring** | Behavior Rules | 8 | Behavior detection rule management |
| **Monitoring** | ThreatInsight | 2 | Threat detection configuration |
| **Monitoring** | Sessions | 5 | Session lifecycle and revocation |
| **Infrastructure** | Network Zones | 8 | IP/dynamic zone management |
| **Infrastructure** | Event Hooks | 9 | Webhook event hook management |
| **Infrastructure** | Identity Providers | 8 | External IdP configuration |
| **Infrastructure** | Devices | 5 | Device inventory and management |
| **Infrastructure** | Brands | 12 | Brand, theme, and email customization |
```

**Step 2: Verify the overview table renders correctly**

Count: should be 19 rows, tool counts should sum correctly.

---

### Task 3: Add Identity Management Module Tables

**Step 1: Add Users table**

Append after the overview table:

```markdown
---

### Identity Management

#### Users

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_users` | List all users with pagination | `search`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |
| `get_user` | Get a user by ID | `user_id` |
| `create_user` | Create a new user | `profile` |
| `update_user` | Update user profile | `user_id`, `profile` |
| `deactivate_user` | Deactivate a user | `user_id` |
| `delete_deactivated_user` | Permanently delete a deactivated user | `user_id` |
| `activate_user` | Activate a user | `user_id` |
| `reactivate_user` | Reactivate a deprovisioned user | `user_id` |
| `suspend_user` | Suspend a user | `user_id` |
| `unsuspend_user` | Unsuspend a user | `user_id` |
| `unlock_user` | Unlock a locked-out user | `user_id` |
| `expire_password` | Expire a user's password | `user_id` |
| `expire_password_with_temp_password` | Expire password and generate temporary | `user_id` |
| `reset_password` | Reset a user's password | `user_id`, `send_email` |
| `list_user_groups` | List groups a user belongs to | `user_id`, `limit`, `after`, `fetch_all` |
| `list_user_apps` | List apps linked to a user | `user_id`, `limit`, `after`, `fetch_all` |
| `get_user_profile_attributes` | List all supported profile attributes | _(none)_ |

#### Groups

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_groups` | List all groups with pagination | `search`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |
| `get_group` | Get a group by ID | `group_id` |
| `create_group` | Create a new group | `profile` |
| `update_group` | Update group profile | `group_id`, `profile` |
| `delete_group` | Delete a group (confirmation required) | `group_id` |
| `confirm_delete_group` | Confirm and execute group deletion | `group_id`, `confirmation` |
| `list_group_users` | List users in a group | `group_id`, `limit`, `after`, `fetch_all` |
| `list_group_apps` | List apps assigned to a group | `group_id` |
| `add_user_to_group` | Add a user to a group | `group_id`, `user_id` |
| `remove_user_from_group` | Remove a user from a group | `group_id`, `user_id` |

#### Schemas

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_user_schema` | Get default user profile schema | _(none)_ |
| `get_user_schema_by_type` | Get schema for a specific user type | `type_id` |
| `list_user_types` | List all user types | _(none)_ |
| `add_user_schema_property` | Add a custom attribute | `property_name`, `type_id`, `property_config` |
| `update_user_schema_property` | Update a custom attribute | `property_name`, `type_id`, `property_config` |
| `remove_user_schema_property` | Remove a custom attribute | `property_name`, `type_id` |
| `get_app_user_schema` | Get app-specific user schema | `app_id` |
| `update_app_user_schema` | Update app-specific user schema | `app_id`, `schema_config` |
```

---

### Task 4: Add Application Management Module Tables

**Step 1: Add Applications and Trusted Origins tables**

```markdown
### Application Management

#### Applications

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_applications` | List all applications with pagination | `q`, `filter_expr`, `expand`, `limit`, `after`, `fetch_all` |
| `get_application` | Get an application by ID | `app_id`, `expand` |
| `create_application` | Create a new application | `app_config`, `activate` |
| `update_application` | Update an application | `app_id`, `app_config` |
| `delete_application` | Delete an application (confirmation required) | `app_id` |
| `confirm_delete_application` | Confirm and execute app deletion | `app_id`, `confirmation` |
| `activate_application` | Activate an application | `app_id` |
| `deactivate_application` | Deactivate an application | `app_id` |
| `list_application_users` | List users assigned to an app | `app_id`, `limit`, `after`, `fetch_all` |
| `get_application_user` | Get a specific app user | `app_id`, `user_id` |
| `assign_user_to_application` | Assign a user to an app | `app_id`, `user_id`, `app_user_config` |
| `remove_user_from_application` | Remove a user from an app | `app_id`, `user_id` |
| `list_application_groups` | List groups assigned to an app | `app_id`, `limit`, `after`, `fetch_all` |
| `get_application_group` | Get a specific app group | `app_id`, `group_id` |
| `assign_group_to_application` | Assign a group to an app | `app_id`, `group_id` |
| `remove_group_from_application` | Remove a group from an app | `app_id`, `group_id` |

#### Trusted Origins

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_trusted_origins` | List all trusted origins | `q`, `limit`, `after`, `fetch_all` |
| `get_trusted_origin` | Get a trusted origin by ID | `origin_id` |
| `create_trusted_origin` | Create a new trusted origin | `name`, `origin`, `scopes` |
| `update_trusted_origin` | Update a trusted origin | `origin_id`, `name`, `scopes` |
| `delete_trusted_origin` | Delete a trusted origin (confirmation required) | `origin_id` |
| `confirm_delete_trusted_origin` | Confirm and execute deletion | `origin_id`, `confirmation` |
| `activate_trusted_origin` | Activate a trusted origin | `origin_id` |
| `deactivate_trusted_origin` | Deactivate a trusted origin | `origin_id` |
```

---

### Task 5: Add Security & Access Control Module Tables

**Step 1: Add Policies, Roles, Auth Servers, Authenticators, Factors tables**

```markdown
### Security & Access Control

#### Policies

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_policies` | List all policies | `type`, `status`, `q`, `limit`, `after` |
| `get_policy` | Get a policy by ID | `policy_id` |
| `create_policy` | Create a new policy | `policy_data` |
| `update_policy` | Update a policy | `policy_id`, `policy_data` |
| `delete_policy` | Delete a policy | `policy_id` |
| `activate_policy` | Activate a policy | `policy_id` |
| `deactivate_policy` | Deactivate a policy | `policy_id` |
| `list_policy_rules` | List rules for a policy | `policy_id` |
| `get_policy_rule` | Get a specific policy rule | `policy_id`, `rule_id` |
| `create_policy_rule` | Create a rule for a policy | `policy_id`, `rule_data` |
| `update_policy_rule` | Update a policy rule | `policy_id`, `rule_id`, `rule_data` |
| `delete_policy_rule` | Delete a policy rule | `policy_id`, `rule_id` |
| `activate_policy_rule` | Activate a policy rule | `policy_id`, `rule_id` |
| `deactivate_policy_rule` | Deactivate a policy rule | `policy_id`, `rule_id` |

#### Roles

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_roles` | List all available admin role types | _(none)_ |
| `list_user_roles` | List roles assigned to a user | `user_id` |
| `list_group_roles` | List roles assigned to a group | `group_id` |
| `assign_role_to_user` | Assign an admin role to a user | `user_id`, `role_type` |
| `unassign_role_from_user` | Remove a role from a user | `user_id`, `role_id` |
| `assign_role_to_group` | Assign an admin role to a group | `group_id`, `role_type` |
| `unassign_role_from_group` | Remove a role from a group | `group_id`, `role_id` |
| `list_user_role_targets` | List targets for a scoped role | `user_id`, `role_id`, `target_type` |
| `add_user_role_target` | Add a target to a scoped role | `user_id`, `role_id`, `target_type`, `target_id` |
| `remove_user_role_target` | Remove a target from a scoped role | `user_id`, `role_id`, `target_type`, `target_id` |

#### Authorization Servers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_authorization_servers` | List all authorization servers | `q`, `limit`, `after`, `fetch_all` |
| `get_authorization_server` | Get an auth server by ID | `auth_server_id` |
| `create_authorization_server` | Create a new auth server | `name`, `description`, `audiences` |
| `update_authorization_server` | Update an auth server | `auth_server_id`, `name`, `description`, `audiences` |
| `delete_authorization_server` | Delete an auth server (confirmation required) | `auth_server_id` |
| `confirm_delete_authorization_server` | Confirm and execute deletion | `auth_server_id`, `confirmation` |
| `activate_authorization_server` | Activate an auth server | `auth_server_id` |
| `deactivate_authorization_server` | Deactivate an auth server | `auth_server_id` |
| `list_auth_server_policies` | List policies for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_policy` | Create a policy for an auth server | `auth_server_id`, `policy_config` |
| `list_auth_server_scopes` | List scopes for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_scope` | Create a scope for an auth server | `auth_server_id`, `name`, `description` |
| `list_auth_server_claims` | List claims for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_claim` | Create a claim for an auth server | `auth_server_id`, `name`, `claim_type`, `value` |

#### Authenticators

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_authenticators` | List all authenticators | _(none)_ |
| `get_authenticator` | Get authenticator details | `authenticator_id` |
| `activate_authenticator` | Activate an authenticator | `authenticator_id` |
| `deactivate_authenticator` | Deactivate an authenticator | `authenticator_id` |
| `list_authenticator_methods` | List methods for an authenticator | `authenticator_id` |
| `get_authenticator_method` | Get a specific method | `authenticator_id`, `method_type` |
| `activate_authenticator_method` | Activate a method | `authenticator_id`, `method_type` |
| `deactivate_authenticator_method` | Deactivate a method | `authenticator_id`, `method_type` |

#### Factors

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_user_factors` | List MFA factors for a user | `user_id` |
| `get_user_factor` | Get a specific factor | `user_id`, `factor_id` |
| `enroll_factor` | Enroll a new MFA factor | `user_id`, `factor_type`, `provider`, `profile` |
| `activate_factor` | Activate an enrolled factor | `user_id`, `factor_id`, `pass_code` |
| `reset_factor` | Remove a factor | `user_id`, `factor_id` |
| `verify_factor` | Verify a factor challenge | `user_id`, `factor_id`, `pass_code` |
```

---

### Task 6: Add Security Monitoring Module Tables

**Step 1: Add System Logs, Behavior Rules, ThreatInsight, Sessions tables**

```markdown
### Security Monitoring

#### System Logs

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_logs` | Retrieve system logs with filtering | `since`, `until`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |

#### Behavior Detection Rules

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_behavior_rules` | List all behavior detection rules | _(none)_ |
| `get_behavior_rule` | Get a behavior rule by ID | `behavior_id` |
| `create_behavior_rule` | Create a new behavior rule | `name`, `behavior_type`, `settings` |
| `update_behavior_rule` | Update a behavior rule | `behavior_id`, `name`, `behavior_type`, `settings` |
| `delete_behavior_rule` | Delete a behavior rule (confirmation required) | `behavior_id` |
| `confirm_delete_behavior_rule` | Confirm and execute deletion | `behavior_id`, `confirmation` |
| `activate_behavior_rule` | Activate a behavior rule | `behavior_id` |
| `deactivate_behavior_rule` | Deactivate a behavior rule | `behavior_id` |

#### ThreatInsight

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_threat_insight_configuration` | Get current ThreatInsight config | _(none)_ |
| `update_threat_insight_configuration` | Update ThreatInsight config | `action`, `exclude_zones` |

#### Sessions

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_session` | Get a session by ID | `session_id` |
| `create_session` | Create a new session | `session_token` |
| `refresh_session` | Refresh/extend a session | `session_id` |
| `close_session` | Close a specific session | `session_id` |
| `revoke_user_sessions` | Revoke all sessions for a user | `user_id` |
```

---

### Task 7: Add Infrastructure & Integrations Module Tables

**Step 1: Add Network Zones, Event Hooks, Identity Providers, Devices, Brands tables**

```markdown
### Infrastructure & Integrations

#### Network Zones

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_network_zones` | List all network zones | `q`, `limit`, `after`, `fetch_all` |
| `get_network_zone` | Get a network zone by ID | `zone_id` |
| `create_network_zone` | Create a new network zone | `name`, `zone_type`, `gateways`, `proxies` |
| `update_network_zone` | Update a network zone | `zone_id`, `name`, `gateways`, `proxies` |
| `delete_network_zone` | Delete a zone (confirmation required) | `zone_id` |
| `confirm_delete_network_zone` | Confirm and execute deletion | `zone_id`, `confirmation` |
| `activate_network_zone` | Activate a network zone | `zone_id` |
| `deactivate_network_zone` | Deactivate a network zone | `zone_id` |

#### Event Hooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_event_hooks` | List all event hooks | _(none)_ |
| `get_event_hook` | Get an event hook by ID | `event_hook_id` |
| `create_event_hook` | Create a new event hook | `name`, `url`, `events`, `headers` |
| `update_event_hook` | Update an event hook | `event_hook_id`, `name`, `url`, `events`, `headers` |
| `delete_event_hook` | Delete an event hook (confirmation required) | `event_hook_id` |
| `confirm_delete_event_hook` | Confirm and execute deletion | `event_hook_id`, `confirmation` |
| `activate_event_hook` | Activate an event hook | `event_hook_id` |
| `deactivate_event_hook` | Deactivate an event hook | `event_hook_id` |
| `verify_event_hook` | Verify an event hook endpoint | `event_hook_id` |

#### Identity Providers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_identity_providers` | List all identity providers | `q`, `type_filter`, `limit`, `after`, `fetch_all` |
| `get_identity_provider` | Get an IdP by ID | `idp_id` |
| `create_identity_provider` | Create a new IdP | `name`, `idp_type`, `protocol`, `policy` |
| `update_identity_provider` | Update an IdP | `idp_id`, `name`, `protocol`, `policy` |
| `delete_identity_provider` | Delete an IdP (confirmation required) | `idp_id` |
| `confirm_delete_identity_provider` | Confirm and execute deletion | `idp_id`, `confirmation` |
| `activate_identity_provider` | Activate an IdP | `idp_id` |
| `deactivate_identity_provider` | Deactivate an IdP | `idp_id` |

#### Devices

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_devices` | List all devices | _(none)_ |
| `get_device` | Get a device by ID | `device_id` |
| `delete_device` | Delete a device (confirmation required) | `device_id` |
| `confirm_delete_device` | Confirm and execute deletion | `device_id`, `confirmation` |
| `list_user_devices` | List devices for a user | `user_id` |

#### Brands

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_brands` | List all brands | _(none)_ |
| `get_brand` | Get a brand by ID | `brand_id` |
| `update_brand` | Update a brand | `brand_id`, `brand_config` |
| `list_brand_themes` | List themes for a brand | `brand_id` |
| `get_brand_theme` | Get a specific theme | `brand_id`, `theme_id` |
| `update_brand_theme` | Update a brand theme | `brand_id`, `theme_id`, `theme_config` |
| `upload_brand_logo` | Upload a logo image | `brand_id`, `theme_id`, `logo_file_path` |
| `upload_brand_favicon` | Upload a favicon image | `brand_id`, `theme_id`, `favicon_file_path` |
| `get_email_template` | Get an email template | `brand_id`, `template_name` |
| `update_email_template` | Update an email template | `brand_id`, `template_name`, `template_config` |
| `get_signin_page` | Get sign-in page customization | `brand_id` |
| `update_signin_page` | Update sign-in page customization | `brand_id`, `page_config` |
```

---

### Task 8: Merge Duplicate Debug Section and Update Key Features

**Files:**
- Modify: `README.md:350-362` (standalone Debug Logs section)
- Modify: `README.md:33` (Key Features bullet)

**Step 1: Remove standalone Debug Logs section**

Delete the entire `## 📋 Debug Logs` section (lines 350-362) since this content already exists in the Troubleshooting section (lines 317-319).

**Step 2: Update Key Features bullet**

Change:
```markdown
* **Comprehensive Tool Support:** Full CRUD operations for users, groups, applications, policies, and more.
```
To:
```markdown
* **Comprehensive Tool Support:** 169 tools across 19 domains — users, groups, applications, policies, security monitoring, and more.
```

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: restructure README with complete tool catalog for all 19 modules"
```

---

### Task 9: Final Verification

**Step 1: Verify README renders correctly**

Read the full README and verify:
- Overview table has 19 rows
- All 5 category sections have correct module tables
- No broken markdown table formatting
- Debug Logs section removed (no duplicate)
- Key Features bullet updated

**Step 2: Verify CLAUDE.md**

Read CLAUDE.md and confirm 19 modules in the tool table.

**Step 3: Push**

```bash
git push
```
