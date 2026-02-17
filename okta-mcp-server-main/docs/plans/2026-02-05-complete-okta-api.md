# Okta MCP Server Expansion - Complete API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task with fresh subagent per task and code review between tasks.

**Goal:** Expand the existing Okta MCP server to be a complete Okta API MCP server with full coverage of users, applications, authorization servers, identity providers, factors, network zones, trusted origins, roles, schemas, and brands.

**Architecture:** Follows existing FastMCP tool pattern with `@mcp.tool()` decorators, async/await, Context-based auth access, standardized pagination/response utilities, and two-step deletion confirmation for destructive operations.

**Tech Stack:** Python 3.8+, FastMCP, Okta Python SDK, loguru logging, pytest for testing

**Scope:** All 10 phases - 92 new tools across 13 modules (40 → 132 total tools)

**Execution:** Subagent-driven - fresh subagent per task with code review between tasks

---

## Phase 1: Complete Users Module (High Priority)

### Task 1.1: Add User Lifecycle Operations

**Files:**
- Modify: `src/okta_mcp_server/tools/users/users.py`
- Modify: `src/okta_mcp_server/tools/users/__init__.py`

**Functions to add (5):**
- `activate_user(user_id, ctx)` - API: `client.activate_user(user_id)` - Activate STAGED/PROVISIONED users
- `reactivate_user(user_id, ctx)` - API: `client.reactivate_user(user_id)` - Reactivate DEPROVISIONED users
- `suspend_user(user_id, ctx)` - API: `client.suspend_user(user_id)` - Temporarily suspend active users
- `unsuspend_user(user_id, ctx)` - API: `client.unsuspend_user(user_id)` - Restore suspended users
- `unlock_user(user_id, ctx)` - API: `client.unlock_user(user_id)` - Unlock LOCKED_OUT users

**Pattern:** Copy `deactivate_user` pattern from lines 256-287.

---

### Task 1.2: Add Password Management Operations

**Files:**
- Modify: `src/okta_mcp_server/tools/users/users.py`

**Functions to add (3):**
- `expire_password(user_id, ctx)` - API: `client.expire_password(user_id)` - Force password reset on next login
- `expire_password_with_temp_password(user_id, ctx)` - API: `client.expire_password(user_id, {"tempPassword": True})` - Returns temporary password
- `reset_password(user_id, send_email=True, ctx)` - API: `client.reset_password(user_id, {"sendEmail": send_email})` - Returns reset link

---

### Task 1.3: Add User Relationship Queries

**Files:**
- Modify: `src/okta_mcp_server/tools/users/users.py`

**Functions to add (2):**
- `list_user_groups(user_id, fetch_all, after, limit, ctx)` - API: `client.list_user_groups(user_id, query_params)` - Paginated groups list
- `list_user_apps(user_id, fetch_all, after, limit, ctx)` - API: `client.list_app_links(user_id)` - Paginated apps list

**Pattern:** Copy `list_users` pagination pattern from lines 19-114.

---

### Task 1.4: Update Users Exports and Tests

**Files:**
- Modify: `src/okta_mcp_server/tools/users/__init__.py`
- Modify: `tests/test_users.py`
- Modify: `tests/conftest.py`

Add exports and tests for all 10 new functions.

---

## Phase 2: Complete Applications Module (High Priority)

### Task 2.1: Add Application User Assignment Operations

**Files:**
- Modify: `src/okta_mcp_server/tools/applications/applications.py`

**Functions to add (4):**
- `list_application_users(app_id, fetch_all, after, limit, ctx)` - Paginated users assigned to app
- `get_application_user(app_id, user_id, ctx)` - Specific user assignment details
- `assign_user_to_application(app_id, user_id, app_user_config, ctx)` - Assign user to app
- `remove_user_from_application(app_id, user_id, ctx)` - Unassign user from app

---

### Task 2.2: Add Application Group Assignment Operations

**Files:**
- Modify: `src/okta_mcp_server/tools/applications/applications.py`

**Functions to add (4):**
- `list_application_groups(app_id, fetch_all, after, limit, ctx)` - Paginated groups assigned to app
- `get_application_group(app_id, group_id, ctx)` - Specific group assignment details
- `assign_group_to_application(app_id, group_id, ctx)` - Assign group to app
- `remove_group_from_application(app_id, group_id, ctx)` - Unassign group from app

---

### Task 2.3: Update Applications Exports and Tests

**Files:**
- Modify: `src/okta_mcp_server/tools/applications/__init__.py`
- Create: `tests/test_applications.py`

---

## Phase 3: Authorization Servers Module (New)

### Task 3.1: Create Auth Servers Module

**Files:**
- Create: `src/okta_mcp_server/tools/auth_servers/__init__.py`
- Create: `src/okta_mcp_server/tools/auth_servers/auth_servers.py`

**Functions (14):**
- CRUD: `list_authorization_servers`, `get_authorization_server`, `create_authorization_server`, `update_authorization_server`
- Deletion: `delete_authorization_server` (confirmation), `confirm_delete_authorization_server`
- Lifecycle: `activate_authorization_server`, `deactivate_authorization_server`
- Policies: `list_auth_server_policies`, `create_auth_server_policy`
- Scopes: `list_auth_server_scopes`, `create_auth_server_scope`
- Claims: `list_auth_server_claims`, `create_auth_server_claim`

---

### Task 3.2: Register Auth Servers Module

**Files:**
- Modify: `src/okta_mcp_server/server.py` (add import in main())
- Create: `tests/test_auth_servers.py`

---

## Phase 4: Identity Providers Module (New)

### Task 4.1: Create Identity Providers Module

**Files:**
- Create: `src/okta_mcp_server/tools/identity_providers/__init__.py`
- Create: `src/okta_mcp_server/tools/identity_providers/identity_providers.py`

**Functions (8):**
- CRUD: `list_identity_providers`, `get_identity_provider`, `create_identity_provider`, `update_identity_provider`
- Deletion: `delete_identity_provider` (confirmation), `confirm_delete_identity_provider`
- Lifecycle: `activate_identity_provider`, `deactivate_identity_provider`

---

### Task 4.2: Register Identity Providers Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_identity_providers.py`

---

## Phase 5: Factors/MFA Module (New)

### Task 5.1: Create Factors Module

**Files:**
- Create: `src/okta_mcp_server/tools/factors/__init__.py`
- Create: `src/okta_mcp_server/tools/factors/factors.py`

**Functions (6):**
- `list_user_factors(user_id, ctx)` - List enrolled factors
- `get_user_factor(user_id, factor_id, ctx)` - Get factor details
- `enroll_factor(user_id, factor_type, provider, profile, ctx)` - Enroll new MFA
- `activate_factor(user_id, factor_id, pass_code, ctx)` - Activate enrolled factor
- `reset_factor(user_id, factor_id, ctx)` - Reset/remove factor
- `verify_factor(user_id, factor_id, pass_code, ctx)` - Verify factor challenge

---

### Task 5.2: Register Factors Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_factors.py`

---

## Phase 6: Network Zones Module (New)

### Task 6.1: Create Network Zones Module

**Files:**
- Create: `src/okta_mcp_server/tools/network_zones/__init__.py`
- Create: `src/okta_mcp_server/tools/network_zones/network_zones.py`

**Functions (8):**
- CRUD: `list_network_zones`, `get_network_zone`, `create_network_zone`, `update_network_zone`
- Deletion: `delete_network_zone` (confirmation), `confirm_delete_network_zone`
- Lifecycle: `activate_network_zone`, `deactivate_network_zone`

---

### Task 6.2: Register Network Zones Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_network_zones.py`

---

## Phase 7: Trusted Origins Module (New)

### Task 7.1: Create Trusted Origins Module

**Files:**
- Create: `src/okta_mcp_server/tools/trusted_origins/__init__.py`
- Create: `src/okta_mcp_server/tools/trusted_origins/trusted_origins.py`

**Functions (8):**
- CRUD: `list_trusted_origins`, `get_trusted_origin`, `create_trusted_origin`, `update_trusted_origin`
- Deletion: `delete_trusted_origin` (confirmation), `confirm_delete_trusted_origin`
- Lifecycle: `activate_trusted_origin`, `deactivate_trusted_origin`

---

### Task 7.2: Register Trusted Origins Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_trusted_origins.py`

---

## Phase 8: Roles/Admin Module (New)

### Task 8.1: Create Roles Module

**Files:**
- Create: `src/okta_mcp_server/tools/roles/__init__.py`
- Create: `src/okta_mcp_server/tools/roles/roles.py`

**Functions (10):**
- `list_roles(ctx)` - List all available admin role types
- `list_user_roles(user_id, ctx)` - List roles assigned to a user
- `list_group_roles(group_id, ctx)` - List roles assigned to a group
- `assign_role_to_user(user_id, role_type, ctx)` - Assign admin role to user (SUPER_ADMIN, ORG_ADMIN, APP_ADMIN, USER_ADMIN, HELP_DESK_ADMIN, READ_ONLY_ADMIN, etc.)
- `unassign_role_from_user(user_id, role_id, ctx)` - Remove role from user
- `assign_role_to_group(group_id, role_type, ctx)` - Assign admin role to group
- `unassign_role_from_group(group_id, role_id, ctx)` - Remove role from group
- `list_user_role_targets(user_id, role_id, ctx)` - List targets (apps/groups) for scoped role
- `add_user_role_target(user_id, role_id, target_type, target_id, ctx)` - Add target to scoped role
- `remove_user_role_target(user_id, role_id, target_type, target_id, ctx)` - Remove target from scoped role

---

### Task 8.2: Register Roles Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_roles.py`

---

## Phase 9: Schemas Module (New)

### Task 9.1: Create Schemas Module

**Files:**
- Create: `src/okta_mcp_server/tools/schemas/__init__.py`
- Create: `src/okta_mcp_server/tools/schemas/schemas.py`

**Functions (8):**
- `get_user_schema(ctx)` - Get the default user profile schema
- `get_user_schema_by_type(type_id, ctx)` - Get schema for a specific user type
- `list_user_types(ctx)` - List all user types
- `add_user_schema_property(type_id, property_name, property_config, ctx)` - Add custom attribute to user schema
- `update_user_schema_property(type_id, property_name, property_config, ctx)` - Update custom attribute
- `remove_user_schema_property(type_id, property_name, ctx)` - Remove custom attribute
- `get_app_user_schema(app_id, ctx)` - Get app-specific user profile schema
- `update_app_user_schema(app_id, schema_config, ctx)` - Update app user schema

---

### Task 9.2: Register Schemas Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_schemas.py`

---

## Phase 10: Brands/Themes Module (New)

### Task 10.1: Create Brands Module

**Files:**
- Create: `src/okta_mcp_server/tools/brands/__init__.py`
- Create: `src/okta_mcp_server/tools/brands/brands.py`

**Functions (12):**
- `list_brands(ctx)` - List all brands in org
- `get_brand(brand_id, ctx)` - Get brand details
- `update_brand(brand_id, brand_config, ctx)` - Update brand settings
- `list_brand_themes(brand_id, ctx)` - List themes for a brand
- `get_brand_theme(brand_id, theme_id, ctx)` - Get theme details
- `update_brand_theme(brand_id, theme_id, theme_config, ctx)` - Update theme (colors, etc.)
- `upload_brand_logo(brand_id, theme_id, logo_file, ctx)` - Upload logo image
- `upload_brand_favicon(brand_id, theme_id, favicon_file, ctx)` - Upload favicon
- `get_email_template(brand_id, template_name, ctx)` - Get email template
- `update_email_template(brand_id, template_name, template_config, ctx)` - Customize email template
- `get_signin_page(brand_id, ctx)` - Get sign-in page customization
- `update_signin_page(brand_id, page_config, ctx)` - Customize sign-in page

---

### Task 10.2: Register Brands Module

**Files:**
- Modify: `src/okta_mcp_server/server.py`
- Create: `tests/test_brands.py`

---

## Summary

| Module | Current | Adding | Total |
|--------|---------|--------|-------|
| Users | 7 | 10 | 17 |
| Groups | 10 | 0 | 10 |
| Applications | 8 | 8 | 16 |
| Policies | 14 | 0 | 14 |
| System Logs | 1 | 0 | 1 |
| Auth Servers | 0 | 14 | 14 |
| Identity Providers | 0 | 8 | 8 |
| Factors | 0 | 6 | 6 |
| Network Zones | 0 | 8 | 8 |
| Trusted Origins | 0 | 8 | 8 |
| Roles/Admin | 0 | 10 | 10 |
| Schemas | 0 | 8 | 8 |
| Brands/Themes | 0 | 12 | 12 |
| **TOTAL** | **40** | **92** | **132** |

---

## Verification

After each phase:
1. `uv run ruff check .` - Lint check
2. `uv run ruff format .` - Format code
3. `uv run pytest tests/test_<module>.py -v` - Module tests
4. `uv run pytest` - All tests
5. `OKTA_LOG_LEVEL=DEBUG uv run okta-mcp-server` - Manual test

---

## Code Pattern Reference

**Standard Tool:**
```python
@mcp.tool()
async def operation_name(param: str, ctx: Context = None) -> dict:
    """Description. Parameters: ... Returns: ..."""
    logger.info(f"Operation for {param}")
    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        result, response, err = await client.operation(param)
        if err:
            logger.error(f"Error: {err}")
            return error_response(str(err))
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception: {e}")
        return error_response(str(e))
```

**Deletion Pattern:**
```python
@mcp.tool()
async def delete_resource(resource_id: str, ctx: Context = None) -> dict:
    return success_response({
        "confirmation_required": True,
        "message": f"To confirm deletion of {resource_id}, please type 'DELETE'",
        "resource_id": resource_id,
    })

@mcp.tool()
async def confirm_delete_resource(resource_id: str, confirmation: str, ctx: Context = None) -> dict:
    if confirmation != "DELETE":
        return error_response("Deletion cancelled.")
    # ... execute deletion
```

**Paginated List Pattern:**
```python
@mcp.tool()
async def list_resources(fetch_all: bool = False, after: str = None, limit: int = None, ctx: Context = None) -> dict:
    # Validate limit (20-100 range)
    query_params = build_query_params(after=after, limit=limit)
    items, response, err = await client.list_resources(query_params)
    if fetch_all and response.has_next():
        all_items, pagination_info = await paginate_all_results(response, items)
        return create_paginated_response(all_items, response, fetch_all_used=True, pagination_info=pagination_info)
    return create_paginated_response(items, response, fetch_all_used=fetch_all)
```
