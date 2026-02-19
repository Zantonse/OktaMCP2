# Phase 2: Operational API Coverage Design

**Date:** 2026-02-19
**Scope:** 5 new tool modules (~26 tools) for operational Okta API coverage
**Goal:** Complete the operational tier of Okta admin APIs, bringing the server from 169 to ~195 tools across 24 modules.

## Modules

### 1. Profile Mappings (`tools/profile_mappings/`) — 3 tools

Attribute mappings between sources (AD, LDAP, apps) and Okta user profiles. Read-heavy — Okta auto-manages mapping lifecycle, so no create/delete.

| Tool | SDK Method | Return | Params |
|------|-----------|--------|--------|
| `list_profile_mappings` | `client.list_profile_mappings(query_params)` | 3-tuple | `source_id`, `target_id`, `after`, `limit` |
| `get_profile_mapping` | `client.get_profile_mapping(mapping_id)` | 3-tuple | `mapping_id` |
| `update_profile_mapping` | `client.update_profile_mapping(mapping_id, body)` | 3-tuple | `mapping_id`, `mapping_config` |

### 2. Inline Hooks (`tools/inline_hooks/`) — 9 tools

Customizable logic injection points: token transform, SAML assertion, password import, user import, telephony, registration.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_inline_hooks` | `client.list_inline_hooks(query_params)` | 3-tuple | Optional `type` filter param |
| `get_inline_hook` | `client.get_inline_hook(id)` | 3-tuple | |
| `create_inline_hook` | `client.create_inline_hook(body)` | 3-tuple | `name`, `hook_type`, `url`, `headers` |
| `update_inline_hook` | `client.update_inline_hook(id, body)` | 3-tuple | `inline_hook_id`, optional fields |
| `delete_inline_hook` | — | sync | Two-step confirmation |
| `confirm_delete_inline_hook` | `client.delete_inline_hook(id)` | 2-tuple | |
| `activate_inline_hook` | `client.activate_inline_hook(id)` | 3-tuple | |
| `deactivate_inline_hook` | `client.deactivate_inline_hook(id)` | 3-tuple | |
| `execute_inline_hook` | `client.execute_inline_hook(id, body)` | 3-tuple | `inline_hook_id`, `payload` |

### 3. Device Assurance (`tools/device_assurance/`) — 6 tools

Device posture policies controlling what devices can access Okta. Core to zero-trust.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_device_assurance_policies` | `client.list_device_assurance_policies()` | 3-tuple | No pagination |
| `get_device_assurance_policy` | `client.get_device_assurance_policy(id)` | 3-tuple | |
| `create_device_assurance_policy` | `client.create_device_assurance_policy(body)` | 3-tuple | `name`, `platform`, `policy_config` |
| `update_device_assurance_policy` | `client.replace_device_assurance_policy(id, body)` | 3-tuple | |
| `delete_device_assurance_policy` | — | sync | Two-step confirmation |
| `confirm_delete_device_assurance_policy` | `client.delete_device_assurance_policy(id)` | 2-tuple | |

### 4. Features (`tools/features/`) — 4 tools

Org feature flag management — enable/disable Okta features.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_features` | `client.list_features()` | 3-tuple | No pagination |
| `get_feature` | `client.get_feature(id)` | 3-tuple | |
| `enable_feature` | `client.update_feature_lifecycle(id, "enable", mode)` | 3-tuple | `feature_id`, `mode` |
| `disable_feature` | `client.update_feature_lifecycle(id, "disable", mode)` | 3-tuple | `feature_id`, `mode` |

### 5. Org Settings (`tools/org_settings/`) — 4 tools

Org-level configuration: name, website, support contact info.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `get_org_settings` | `client.get_org_settings()` | 3-tuple | No params |
| `update_org_settings` | `client.partial_update_org_setting(body)` | 3-tuple | `settings` dict |
| `get_org_contact_types` | `client.get_org_contact_types()` | 3-tuple | No params |
| `get_org_contact_user` | `client.get_org_contact_user(contact_type)` | 3-tuple | `contact_type` |

## Patterns

All modules follow established conventions:
- `@mcp.tool()` decorator, `ctx: Context` first param
- `validate_okta_id()` on all ID params
- `sanitize_error()` on all error paths
- `success_response()` / `error_response()` return format
- Two-step deletion with sync `delete_*` + async `confirm_delete_*`
- Apache 2.0 license headers
- Tests with MockOktaClient in conftest.py
- Registration in server.py

## Deliverables

1. 5 new tool modules (~26 tools)
2. ~60-80 new tests
3. Updated README.md (overview table + 5 new module tables)
4. Updated CLAUDE.md (5 new rows)
5. Git commit and push
