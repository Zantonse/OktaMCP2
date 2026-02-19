# Phase 3: Core Admin Gaps Design

**Date:** 2026-02-19
**Scope:** 7 new tool modules (~33 tools) for operational completeness
**Goal:** Fill the most common admin workflow gaps, bringing the server from 195 to ~228 tools across 31 modules.

## Modules

### 1. Group Rules (`tools/group_rules/`) — 7 tools

Dynamic group membership based on user attribute expressions. Completes the groups story.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_group_rules` | `client.list_group_rules(query_params)` | 3-tuple | Optional `limit`, `after`, `expand` |
| `get_group_rule` | `client.get_group_rule(rule_id)` | 3-tuple | |
| `create_group_rule` | `client.create_group_rule(body)` | 3-tuple | `name`, `conditions`, `actions` |
| `update_group_rule` | `client.update_group_rule(rule_id, body)` | 3-tuple | |
| `delete_group_rule` | — | sync | Two-step confirmation |
| `activate_group_rule` | `client.activate_group_rule(rule_id)` | 2-tuple | |
| `deactivate_group_rule` | `client.deactivate_group_rule(rule_id)` | 2-tuple | |

### 2. Linked Objects (`tools/linked_objects/`) — 5 tools

Relationship definitions between users (manager/subordinate, mentor/mentee, case worker/client).

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_linked_object_definitions` | `client.list_linked_object_definitions()` | 3-tuple | |
| `get_linked_object_definition` | `client.get_linked_object_definition(name)` | 3-tuple | `name` is string, not Okta ID |
| `create_linked_object_definition` | `client.add_linked_object_definition(body)` | 3-tuple | `primary`, `associated` objects |
| `delete_linked_object_definition` | `client.delete_linked_object_definition(name)` | 2-tuple | Two-step confirmation |
| `get_user_linked_objects` | `client.get_linked_objects_for_user(user_id, relationship_name)` | 3-tuple | `user_id`, `relationship_name` |

### 3. User Types (`tools/user_types/`) — 5 tools

Custom user types (employee, contractor, partner) with distinct profile schemas.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_user_types` | `client.list_user_types()` | 3-tuple | No params |
| `get_user_type` | `client.get_user_type(type_id)` | 3-tuple | |
| `create_user_type` | `client.create_user_type(body)` | 3-tuple | `name`, `display_name`, `description` |
| `update_user_type` | `client.update_user_type(type_id, body)` | 3-tuple | |
| `delete_user_type` | `client.delete_user_type(type_id)` | 2-tuple | Two-step confirmation |

### 4. Custom Domains (`tools/custom_domains/`) — 5 tools

Custom domain configurations for Okta sign-in pages and white-labeling.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_custom_domains` | `client.list_custom_domains()` | 3-tuple | |
| `get_custom_domain` | `client.get_custom_domain(domain_id)` | 3-tuple | |
| `create_custom_domain` | `client.create_custom_domain(body)` | 3-tuple | `domain`, `certificate_source_type` |
| `delete_custom_domain` | — | sync | Two-step confirmation |
| `verify_custom_domain` | `client.verify_custom_domain(domain_id)` | 3-tuple | |

### 5. Email Domains (`tools/email_domains/`) — 4 tools

Sender domain configuration for Okta-sent emails.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_email_domains` | `client.list_email_domains()` | 3-tuple | |
| `get_email_domain` | `client.get_email_domain(domain_id)` | 3-tuple | |
| `create_email_domain` | `client.create_email_domain(body)` | 3-tuple | `domain`, `display_name`, `user_name` |
| `delete_email_domain` | `client.delete_email_domain(domain_id)` | 2-tuple | Two-step confirmation |

### 6. Rate Limit Settings (`tools/rate_limits/`) — 3 tools

API rate limit visibility and configuration.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `get_rate_limit_settings` | `client.get_rate_limit_settings_admin_notifications()` | 3-tuple | No params |
| `get_per_client_rate_limit` | `client.get_per_client_rate_limit_settings()` | 3-tuple | No params |
| `update_per_client_rate_limit` | `client.replace_per_client_rate_limit_settings(body)` | 3-tuple | `settings` dict |

### 7. API Tokens (`tools/api_tokens/`) — 4 tools

SSWS API token lifecycle management and governance.

| Tool | SDK Method | Return | Notes |
|------|-----------|--------|-------|
| `list_api_tokens` | `client.list_api_tokens()` | 3-tuple | |
| `get_api_token` | `client.get_api_token(token_id)` | 3-tuple | |
| `revoke_api_token` | — | sync | Two-step confirmation |
| `confirm_revoke_api_token` | `client.revoke_api_token(token_id)` | 2-tuple | |

## Patterns

All modules follow established conventions from Phase 1 and 2:
- `@mcp.tool()` decorator, `ctx: Context` first param
- `validate_okta_id()` on all ID params
- `sanitize_error()` on all error paths
- `success_response()` / `error_response()` return format
- Two-step deletion/revocation with sync `delete_*` + async `confirm_delete_*`
- Apache 2.0 license headers
- Tests with MockOktaClient in conftest.py
- Registration in server.py

## Deliverables

1. 7 new tool modules (~33 tools)
2. ~70-90 new tests
3. Updated README.md (overview table + 7 new module tables)
4. Updated CLAUDE.md (7 new rows)
5. Git commit and push
