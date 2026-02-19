# Phase 2: Operational API Coverage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Add 5 operational API modules (~26 tools) to the Okta MCP Server.

**Architecture:** Each module follows the established Phase 1 pattern: `@mcp.tool()` decorators, Context-first params, validate_okta_id(), sanitize_error(), two-step deletion confirmation where applicable. Tests use MockOktaClient fixtures. All modules registered in server.py and documented in README/CLAUDE.md.

**Tech Stack:** Python 3.12+, FastMCP, Okta SDK, pytest

---

## Reference Patterns

All 5 modules follow these established patterns from Phase 1 (sessions, event_hooks, devices, threat_insight, behaviors):

**Tool function pattern:**
```python
@mcp.tool()
async def tool_name(ctx: Context, param1: str, ...) -> dict:
    """Docstring with Parameters and Returns sections."""
    logger.info("Starting operation...")

    # Validate IDs if present
    valid, err_msg = validate_okta_id(param_id, "param_id")
    if not valid:
        return error_response(err_msg)

    manager = ctx.request_context.lifespan_context.okta_auth_manager

    try:
        client = await get_okta_client(manager)
        result, _, err = await client.sdk_method(...)

        if err:
            logger.error(f"Okta API error: {err}")
            return error_response(sanitize_error(err))

        logger.info("Success")
        return success_response(result)
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        return error_response(sanitize_error(e))
```

**Two-step deletion pattern (from network_zones, devices):**
```python
@mcp.tool()
def delete_resource(ctx: Context, resource_id: str) -> dict:
    """NOT async — returns confirmation message."""
    logger.warning(f"Deletion requested for {resource_id}")
    valid, err_msg = validate_okta_id(resource_id, "resource_id")
    if not valid:
        return error_response(err_msg)
    return success_response({
        "confirmation_required": True,
        "message": f"To confirm deletion of {resource_id}, please type 'DELETE'",
        "resource_id": resource_id,
    })

@mcp.tool()
async def confirm_delete_resource(ctx: Context, resource_id: str, confirmation: str) -> dict:
    """Async — executes deletion after confirmation."""
    logger.info(f"Processing deletion confirmation for {resource_id}")
    valid, err_msg = validate_okta_id(resource_id, "resource_id")
    if not valid:
        return error_response(err_msg)
    if confirmation != "DELETE":
        return error_response("Deletion cancelled.")

    manager = ctx.request_context.lifespan_context.okta_auth_manager
    try:
        client = await get_okta_client(manager)
        _, err = await client.delete_method(resource_id)  # 2-tuple return
        if err:
            return error_response(sanitize_error(err))
        return success_response({"message": f"{resource_id} deleted successfully"})
    except Exception as e:
        return error_response(sanitize_error(e))
```

---

## Task 1: Profile Mappings Module

**Files:**
- Create: `src/okta_mcp_server/tools/profile_mappings/__init__.py`
- Create: `src/okta_mcp_server/tools/profile_mappings/profile_mappings.py`
- Create: `tests/test_profile_mappings.py`
- Modify: `tests/conftest.py` (add MockProfileMapping + mock methods)
- Modify: `src/okta_mcp_server/server.py` (add import)

**Tools to implement (3):**
1. `list_profile_mappings` — `client.list_profile_mappings(query_params)`, 3-tuple, supports `source_id`, `target_id`, `after`, `limit`
2. `get_profile_mapping` — `client.get_profile_mapping(mapping_id)`, 3-tuple
3. `update_profile_mapping` — `client.update_profile_mapping(mapping_id, body)`, 3-tuple

**Key notes:**
- No pagination in list (SDK may support, but typically returns all)
- No create/delete — Okta auto-manages mapping lifecycle
- Update takes `mapping_config` with property mappings

**Step 1:** Implement module following Phase 1 patterns
**Step 2:** Add MockProfileMapping to conftest.py with fields: `id`, `source`, `target`, `properties`
**Step 3:** Add 3 mock methods to MockOktaClient (all 3-tuple returns)
**Step 4:** Write 9 tests (3 per tool: success, invalid ID, API error)
**Step 5:** Run tests: `uv run pytest tests/test_profile_mappings.py -v`
**Step 6:** Run lint: `uv run ruff check src/okta_mcp_server/tools/profile_mappings/ tests/test_profile_mappings.py`
**Step 7:** Add import to server.py (alphabetical: after `policies`, before `roles`)
**Step 8:** Commit: `git add ... && git commit -m "feat: add profile mappings tools"`

---

## Task 2: Inline Hooks Module

**Files:**
- Create: `src/okta_mcp_server/tools/inline_hooks/__init__.py`
- Create: `src/okta_mcp_server/tools/inline_hooks/inline_hooks.py`
- Create: `tests/test_inline_hooks.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (9):**
1. `list_inline_hooks` — `client.list_inline_hooks(query_params)`, 3-tuple, optional `type` param
2. `get_inline_hook` — `client.get_inline_hook(inline_hook_id)`, 3-tuple
3. `create_inline_hook` — `client.create_inline_hook(body)`, 3-tuple
4. `update_inline_hook` — `client.update_inline_hook(inline_hook_id, body)`, 3-tuple
5. `delete_inline_hook` — Two-step, `def` (sync), NOT async
6. `confirm_delete_inline_hook` — `async def`, 2-tuple: `client.delete_inline_hook(inline_hook_id)`
7. `activate_inline_hook` — `client.activate_inline_hook(inline_hook_id)`, 3-tuple
8. `deactivate_inline_hook` — `client.deactivate_inline_hook(inline_hook_id)`, 3-tuple
9. `execute_inline_hook` — `client.execute_inline_hook(inline_hook_id, body)`, 3-tuple

**Key notes:**
- Hook types: `com.okta.import.transform`, `com.okta.oauth2.tokens.transform`, etc. (validate in create/update)
- create/update body: `{"name": "...", "type": "...", "version": "1.0.0", "channel": {"type": "HTTP", "version": "1.0.0", "config": {"uri": "...", "headers": [...]}}}`
- execute takes `payload` param for test execution

**Steps:** Same as Task 1 (implement → mock → test → lint → register → commit)

---

## Task 3: Device Assurance Module

**Files:**
- Create: `src/okta_mcp_server/tools/device_assurance/__init__.py`
- Create: `src/okta_mcp_server/tools/device_assurance/device_assurance.py`
- Create: `tests/test_device_assurance.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (6):**
1. `list_device_assurance_policies` — `client.list_device_assurance_policies()`, 3-tuple, no pagination
2. `get_device_assurance_policy` — `client.get_device_assurance_policy(policy_id)`, 3-tuple
3. `create_device_assurance_policy` — `client.create_device_assurance_policy(body)`, 3-tuple
4. `update_device_assurance_policy` — `client.replace_device_assurance_policy(policy_id, body)`, 3-tuple
5. `delete_device_assurance_policy` — Two-step, `def` (sync)
6. `confirm_delete_device_assurance_policy` — `async def`, 2-tuple: `client.delete_device_assurance_policy(policy_id)`

**Key notes:**
- create/update body: `{"name": "...", "platform": "MACOS|WINDOWS|ANDROID|IOS|CHROMEOS", "diskEncryptionType": {...}, "osVersion": {...}, "screenLockType": {...}}`
- Complex nested policy config

**Steps:** Same as Task 1

---

## Task 4: Features Module

**Files:**
- Create: `src/okta_mcp_server/tools/features/__init__.py`
- Create: `src/okta_mcp_server/tools/features/features.py`
- Create: `tests/test_features.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (4):**
1. `list_features` — `client.list_features()`, 3-tuple, no pagination
2. `get_feature` — `client.get_feature(feature_id)`, 3-tuple
3. `enable_feature` — `client.update_feature_lifecycle(feature_id, "enable", mode)`, 3-tuple
4. `disable_feature` — `client.update_feature_lifecycle(feature_id, "disable", mode)`, 3-tuple

**Key notes:**
- enable/disable take optional `mode` param (typically not used, pass None)
- Feature IDs are like `ftxA1B2C3D4E5F6` or semantic names
- No create/delete — features are org-level flags

**Steps:** Same as Task 1

---

## Task 5: Org Settings Module

**Files:**
- Create: `src/okta_mcp_server/tools/org_settings/__init__.py`
- Create: `src/okta_mcp_server/tools/org_settings/org_settings.py`
- Create: `tests/test_org_settings.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (4):**
1. `get_org_settings` — `client.get_org_settings()`, 3-tuple, no params
2. `update_org_settings` — `client.partial_update_org_setting(body)`, 3-tuple
3. `get_org_contact_types` — `client.get_org_contact_types()`, 3-tuple, no params
4. `get_org_contact_user` — `client.get_org_contact_user(contact_type)`, 3-tuple

**Key notes:**
- get_org_settings returns: `{"companyName": "...", "website": "...", "phoneNumber": "...", "address": {...}}`
- update takes partial body (only changed fields)
- contact_type values: `TECHNICAL`, `BILLING` (validate in get_org_contact_user)
- No delete — org settings always exist

**Steps:** Same as Task 1

---

## Task 6: Update Documentation

**Files:**
- Modify: `README.md` (overview table + 5 new module tables)
- Modify: `CLAUDE.md` (tool table)

**Step 1: Update CLAUDE.md**

Add 5 rows to the tool module table (alphabetical order):

After `identity_providers`:
```
| inline_hooks | `tools/inline_hooks/inline_hooks.py` | Inline hook management |
```

After `policies`:
```
| profile_mappings | `tools/profile_mappings/profile_mappings.py` | Profile attribute mappings |
```

After `devices`:
```
| device_assurance | `tools/device_assurance/device_assurance.py` | Device assurance policies |
```

After `event_hooks`:
```
| features | `tools/features/features.py` | Org feature flag management |
```

After `network_zones`:
```
| org_settings | `tools/org_settings/org_settings.py` | Organization settings |
```

**Step 2: Update README overview table**

Change the overview table to add 5 new rows (update tool counts):

In the **Security** section, add after Factors:
```
| **Security** | Device Assurance | 6 | Device posture policy management |
```

In the **Monitoring** section, change the count for Sessions from 5 to match.

In the **Infrastructure** section, add after Identity Providers:
```
| **Infrastructure** | Inline Hooks | 9 | Logic injection hook management |
| **Infrastructure** | Profile Mappings | 3 | Attribute mapping management |
```

Add new **Administration** section after Infrastructure:
```
| **Administration** | Features | 4 | Org feature flag management |
| **Administration** | Org Settings | 4 | Organization configuration |
```

Update the opening line to say "**195 tools across 24 domains**".

**Step 3: Add 5 module tables to README**

Add under the Infrastructure section:

```markdown
#### Inline Hooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_inline_hooks` | List all inline hooks | `type` |
| `get_inline_hook` | Get an inline hook by ID | `inline_hook_id` |
| `create_inline_hook` | Create a new inline hook | `name`, `hook_type`, `url`, `headers` |
| `update_inline_hook` | Update an inline hook | `inline_hook_id`, `name`, `url`, `headers` |
| `delete_inline_hook` | Delete an inline hook (confirmation required) | `inline_hook_id` |
| `confirm_delete_inline_hook` | Confirm and execute deletion | `inline_hook_id`, `confirmation` |
| `activate_inline_hook` | Activate an inline hook | `inline_hook_id` |
| `deactivate_inline_hook` | Deactivate an inline hook | `inline_hook_id` |
| `execute_inline_hook` | Execute an inline hook for testing | `inline_hook_id`, `payload` |

#### Profile Mappings

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_profile_mappings` | List all profile mappings | `source_id`, `target_id`, `after`, `limit` |
| `get_profile_mapping` | Get a profile mapping by ID | `mapping_id` |
| `update_profile_mapping` | Update a profile mapping | `mapping_id`, `mapping_config` |
```

Add under the Security section:

```markdown
#### Device Assurance

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_device_assurance_policies` | List all device assurance policies | _(none)_ |
| `get_device_assurance_policy` | Get a policy by ID | `policy_id` |
| `create_device_assurance_policy` | Create a new policy | `name`, `platform`, `policy_config` |
| `update_device_assurance_policy` | Update a policy | `policy_id`, `policy_config` |
| `delete_device_assurance_policy` | Delete a policy (confirmation required) | `policy_id` |
| `confirm_delete_device_assurance_policy` | Confirm and execute deletion | `policy_id`, `confirmation` |
```

Add new Administration section at the end (before Authentication section):

```markdown
---

### Administration

#### Features

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_features` | List all org features | _(none)_ |
| `get_feature` | Get a feature by ID | `feature_id` |
| `enable_feature` | Enable a feature | `feature_id`, `mode` |
| `disable_feature` | Disable a feature | `feature_id`, `mode` |

#### Org Settings

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_org_settings` | Get organization settings | _(none)_ |
| `update_org_settings` | Update organization settings | `settings` |
| `get_org_contact_types` | Get available contact types | _(none)_ |
| `get_org_contact_user` | Get contact user by type | `contact_type` |
```

**Step 4: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: add Phase 2 modules to README and CLAUDE.md"
```

---

## Task 7: Final Verification and Push

**Step 1: Run full test suite**

```bash
uv run pytest tests/ --tb=short
```

Expected: All tests pass (original 510 + ~60-80 new = ~570-590 total).

**Step 2: Run lint on all new code**

```bash
uv run ruff check src/okta_mcp_server/tools/profile_mappings/ src/okta_mcp_server/tools/inline_hooks/ src/okta_mcp_server/tools/device_assurance/ src/okta_mcp_server/tools/features/ src/okta_mcp_server/tools/org_settings/ tests/test_profile_mappings.py tests/test_inline_hooks.py tests/test_device_assurance.py tests/test_features.py tests/test_org_settings.py
```

Expected: All checks pass.

**Step 3: Verify server.py imports**

Read `src/okta_mcp_server/server.py` and confirm all 5 new modules are imported in alphabetical order.

**Step 4: Push**

```bash
git push
```
