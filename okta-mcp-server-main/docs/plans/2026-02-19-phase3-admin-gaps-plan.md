# Phase 3: Core Admin Gaps Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Add 7 operational API modules (~33 tools) to fill the most common admin workflow gaps.

**Architecture:** Each module follows the established pattern: `@mcp.tool()` decorators, Context-first params, validate_okta_id(), sanitize_error(), two-step deletion confirmation where applicable. Tests use MockOktaClient fixtures. All modules registered in server.py and documented in README/CLAUDE.md.

**Tech Stack:** Python 3.12+, FastMCP, Okta SDK, pytest

---

## Reference Patterns

All 7 modules follow these established patterns (see `tools/device_assurance/device_assurance.py` for the latest reference):

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

**Two-step deletion pattern:**
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

## Task 1: Group Rules Module

**Files:**
- Create: `src/okta_mcp_server/tools/group_rules/__init__.py`
- Create: `src/okta_mcp_server/tools/group_rules/group_rules.py`
- Create: `tests/test_group_rules.py`
- Modify: `tests/conftest.py` (add MockGroupRule + mock methods)
- Modify: `src/okta_mcp_server/server.py` (add import)

**Tools to implement (7):**
1. `list_group_rules` — `client.list_group_rules(query_params)`, 3-tuple, optional `limit`, `after`
2. `get_group_rule` — `client.get_group_rule(rule_id)`, 3-tuple
3. `create_group_rule` — `client.create_group_rule(body)`, 3-tuple, params: `name`, `conditions` (dict), `group_ids` (list of target group IDs)
4. `update_group_rule` — `client.update_group_rule(rule_id, body)`, 3-tuple
5. `delete_group_rule` — Two-step, `def` (sync), NOT async
6. `confirm_delete_group_rule` — `async def`, 2-tuple: `client.delete_group_rule(rule_id)`
7. `activate_group_rule` — `client.activate_group_rule(rule_id)`, 2-tuple (no body returned)
8. `deactivate_group_rule` — `client.deactivate_group_rule(rule_id)`, 2-tuple

**Note:** activate/deactivate return 2-tuples `(_, err)` not 3-tuples.

**Key notes:**
- create body: `{"name": "...", "type": "group_rule", "conditions": {"expression": {"type": "urn:okta:expression:1.0", "value": "..."}}, "actions": {"assignUserToGroups": {"groupIds": [...]}}}`
- For create: take `name: str`, `expression: str`, `group_ids: list` and construct the body
- For update: take `rule_id: str`, `name: str = None`, `expression: str = None`, `group_ids: list = None`

**Mock for conftest.py:**
```python
@dataclass
class MockGroupRule:
    """Mock Okta group rule object."""
    id: str = "0pr1abc123"
    name: str = "Test Group Rule"
    type: str = "group_rule"
    status: str = "ACTIVE"
    conditions: dict = None
    actions: dict = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {"expression": {"type": "urn:okta:expression:1.0", "value": "user.department==\"Engineering\""}}
        if self.actions is None:
            self.actions = {"assignUserToGroups": {"groupIds": ["00g1abc123"]}}
```

**MockOktaClient methods:**
```python
async def list_group_rules(self, query_params=None):
    return [MockGroupRule()], MockOktaResponse(), None

async def get_group_rule(self, rule_id):
    return MockGroupRule(id=rule_id), MockOktaResponse(), None

async def create_group_rule(self, body):
    return MockGroupRule(), MockOktaResponse(), None

async def update_group_rule(self, rule_id, body):
    return MockGroupRule(id=rule_id), MockOktaResponse(), None

async def delete_group_rule(self, rule_id):
    return None, None

async def activate_group_rule(self, rule_id):
    return None, None

async def deactivate_group_rule(self, rule_id):
    return None, None
```

**Tests (~18):** success, invalid_id, api_error for each tool; plus wrong_confirmation for confirm_delete.

**Step 1:** Implement module following patterns above
**Step 2:** Add MockGroupRule to conftest.py + 7 mock methods to MockOktaClient
**Step 3:** Write tests
**Step 4:** Run tests: `uv run pytest tests/test_group_rules.py -v`
**Step 5:** Run lint: `uv run ruff check src/okta_mcp_server/tools/group_rules/ tests/test_group_rules.py`
**Step 6:** Add import to server.py (alphabetical: after `groups`, before `identity_providers`)
**Step 7:** Commit: `git add ... && git commit -m "feat: add group rules tools"`

---

## Task 2: Linked Objects Module

**Files:**
- Create: `src/okta_mcp_server/tools/linked_objects/__init__.py`
- Create: `src/okta_mcp_server/tools/linked_objects/linked_objects.py`
- Create: `tests/test_linked_objects.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (6):**
1. `list_linked_object_definitions` — `client.list_linked_object_definitions()`, 3-tuple, no params
2. `get_linked_object_definition` — `client.get_linked_object_definition(linked_object_name)`, 3-tuple. Note: param is a name string, NOT an Okta ID — do NOT use validate_okta_id
3. `create_linked_object_definition` — `client.add_linked_object_definition(body)`, 3-tuple, params: `primary_name`, `primary_title`, `primary_description`, `associated_name`, `associated_title`, `associated_description`
4. `delete_linked_object_definition` — Two-step, `def` (sync). Note: uses name not ID
5. `confirm_delete_linked_object_definition` — `async def`, `client.delete_linked_object_definition(linked_object_name)`, 2-tuple
6. `get_user_linked_objects` — `client.get_linked_objects_for_user(user_id, relationship_name)`, 3-tuple, validate user_id with validate_okta_id

**Key notes:**
- Linked object definitions use **names** not Okta IDs (e.g., "manager", "reports"). Do NOT validate with validate_okta_id on the name params.
- Only `get_user_linked_objects` has an actual Okta ID (`user_id`) to validate.
- create body: `{"primary": {"name": "...", "title": "...", "description": "...", "type": "USER"}, "associated": {"name": "...", "title": "...", "description": "...", "type": "USER"}}`
- For delete confirmation, validate that the name is non-empty string instead of validate_okta_id.

**Mock:**
```python
@dataclass
class MockLinkedObjectDefinition:
    """Mock Okta linked object definition."""
    primary: dict = None
    associated: dict = None

    def __post_init__(self):
        if self.primary is None:
            self.primary = {"name": "manager", "title": "Manager", "description": "Manager", "type": "USER"}
        if self.associated is None:
            self.associated = {"name": "subordinate", "title": "Subordinate", "description": "Subordinate", "type": "USER"}
```

**MockOktaClient methods:**
```python
async def list_linked_object_definitions(self):
    return [MockLinkedObjectDefinition()], MockOktaResponse(), None

async def get_linked_object_definition(self, name):
    return MockLinkedObjectDefinition(), MockOktaResponse(), None

async def add_linked_object_definition(self, body):
    return MockLinkedObjectDefinition(), MockOktaResponse(), None

async def delete_linked_object_definition(self, name):
    return None, None

async def get_linked_objects_for_user(self, user_id, relationship_name):
    return [MockUser()], MockOktaResponse(), None
```

**Tests (~14):** success + error for each tool; invalid_id for get_user_linked_objects; wrong_confirmation for confirm_delete.

**Steps:** Same as Task 1. Server.py import after `inline_hooks`, before `network_zones`.

---

## Task 3: User Types Module

**Files:**
- Create: `src/okta_mcp_server/tools/user_types/__init__.py`
- Create: `src/okta_mcp_server/tools/user_types/user_types.py`
- Create: `tests/test_user_types.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (5):**
1. `list_user_types` — `client.list_user_types()`, 3-tuple, no params
2. `get_user_type` — `client.get_user_type(type_id)`, 3-tuple
3. `create_user_type` — `client.create_user_type(body)`, 3-tuple, params: `name`, `display_name`, `description`
4. `update_user_type` — `client.update_user_type(type_id, body)`, 3-tuple
5. `delete_user_type` — Two-step: sync `delete_user_type` + async `confirm_delete_user_type`, `client.delete_user_type(type_id)`, 2-tuple

**Key notes:**
- Note: `list_user_types` already exists in schemas.py. This is a SEPARATE module with full CRUD. The existing one in schemas is fine to keep as-is.
- create body: `{"name": "...", "displayName": "...", "description": "..."}`

**Mock:** Already have `MockUserType` in conftest.py. Add CRUD methods:
```python
async def create_user_type(self, body):
    return MockUserType(), MockOktaResponse(), None

async def update_user_type(self, type_id, body):
    return MockUserType(id=type_id), MockOktaResponse(), None

async def delete_user_type(self, type_id):
    return None, None
```

Note: `list_user_types()` and `get_user_type()` may need to be added if not present — check conftest first. `list_user_types` exists (returns `[MockUserType()]`), but `get_user_type` may need adding.

**Tests (~14):** success, invalid_id, error for each; wrong_confirmation for confirm_delete.

**Steps:** Same as Task 1. Server.py import after `users`, at end of list (alphabetically `user_types` comes after `users`).

---

## Task 4: Custom Domains Module

**Files:**
- Create: `src/okta_mcp_server/tools/custom_domains/__init__.py`
- Create: `src/okta_mcp_server/tools/custom_domains/custom_domains.py`
- Create: `tests/test_custom_domains.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (6):**
1. `list_custom_domains` — `client.list_custom_domains()`, 3-tuple, no params
2. `get_custom_domain` — `client.get_custom_domain(domain_id)`, 3-tuple
3. `create_custom_domain` — `client.create_custom_domain(body)`, 3-tuple, params: `domain: str`, `certificate_source_type: str` (OKTA_MANAGED or MANUAL)
4. `delete_custom_domain` — Two-step, `def` (sync)
5. `confirm_delete_custom_domain` — `async def`, `client.delete_custom_domain(domain_id)`, 2-tuple
6. `verify_custom_domain` — `client.verify_custom_domain(domain_id)`, 3-tuple

**Key notes:**
- `certificate_source_type` validation: must be `"OKTA_MANAGED"` or `"MANUAL"`
- create body: `{"domain": "...", "certificateSourceType": "..."}`

**Mock:**
```python
@dataclass
class MockCustomDomain:
    """Mock Okta custom domain object."""
    id: str = "cd1abc123"
    domain: str = "login.example.com"
    certificate_source_type: str = "OKTA_MANAGED"
    validation_status: str = "VERIFIED"
    dns_records: list = None

    def __post_init__(self):
        if self.dns_records is None:
            self.dns_records = [{"record_type": "CNAME", "fqdn": "login.example.com", "values": ["example.customdomains.okta.com"]}]
```

**MockOktaClient methods:**
```python
async def list_custom_domains(self):
    return [MockCustomDomain()], MockOktaResponse(), None

async def get_custom_domain(self, domain_id):
    return MockCustomDomain(id=domain_id), MockOktaResponse(), None

async def create_custom_domain(self, body):
    return MockCustomDomain(), MockOktaResponse(), None

async def delete_custom_domain(self, domain_id):
    return None, None

async def verify_custom_domain(self, domain_id):
    return MockCustomDomain(id=domain_id, validation_status="VERIFIED"), MockOktaResponse(), None
```

**Tests (~16):** success, invalid_id, error for each; invalid_certificate_source_type for create; wrong_confirmation for confirm_delete.

**Steps:** Same as Task 1. Server.py import after `brands`, before `device_assurance`.

---

## Task 5: Email Domains Module

**Files:**
- Create: `src/okta_mcp_server/tools/email_domains/__init__.py`
- Create: `src/okta_mcp_server/tools/email_domains/email_domains.py`
- Create: `tests/test_email_domains.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (5):**
1. `list_email_domains` — `client.list_email_domains()`, 3-tuple, no params
2. `get_email_domain` — `client.get_email_domain(domain_id)`, 3-tuple
3. `create_email_domain` — `client.create_email_domain(body)`, 3-tuple, params: `domain: str`, `display_name: str`, `user_name: str`
4. `delete_email_domain` — Two-step, `def` (sync)
5. `confirm_delete_email_domain` — `async def`, `client.delete_email_domain(domain_id)`, 2-tuple

**Key notes:**
- create body: `{"domain": "...", "displayName": "...", "userName": "..."}`

**Mock:**
```python
@dataclass
class MockEmailDomain:
    """Mock Okta email domain object."""
    id: str = "emd1abc123"
    domain: str = "mail.example.com"
    display_name: str = "Example Mail"
    user_name: str = "noreply"
    validation_status: str = "VERIFIED"
```

**MockOktaClient methods:**
```python
async def list_email_domains(self):
    return [MockEmailDomain()], MockOktaResponse(), None

async def get_email_domain(self, domain_id):
    return MockEmailDomain(id=domain_id), MockOktaResponse(), None

async def create_email_domain(self, body):
    return MockEmailDomain(), MockOktaResponse(), None

async def delete_email_domain(self, domain_id):
    return None, None
```

**Tests (~13):** success, invalid_id, error for each; wrong_confirmation for confirm_delete.

**Steps:** Same as Task 1. Server.py import after `devices`, before `event_hooks`.

---

## Task 6: Rate Limit Settings Module

**Files:**
- Create: `src/okta_mcp_server/tools/rate_limits/__init__.py`
- Create: `src/okta_mcp_server/tools/rate_limits/rate_limits.py`
- Create: `tests/test_rate_limits.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (3):**
1. `get_rate_limit_settings` — `client.get_rate_limit_settings_admin_notifications()`, 3-tuple, no params
2. `get_per_client_rate_limit` — `client.get_per_client_rate_limit_settings()`, 3-tuple, no params
3. `update_per_client_rate_limit` — `client.replace_per_client_rate_limit_settings(body)`, 3-tuple, param: `settings: dict`

**Key notes:**
- No IDs to validate — these are org-level settings
- No delete — settings always exist
- Import only `sanitize_error` from validators (not validate_okta_id)

**Mock:**
```python
@dataclass
class MockRateLimitSettings:
    """Mock Okta rate limit settings object."""
    rate_limit_notification_emails: list = None

    def __post_init__(self):
        if self.rate_limit_notification_emails is None:
            self.rate_limit_notification_emails = ["admin@example.com"]


@dataclass
class MockPerClientRateLimit:
    """Mock Okta per-client rate limit settings."""
    default_mode: str = "PREVIEW"
    use_dynamic_enforcement: bool = False
```

**MockOktaClient methods:**
```python
async def get_rate_limit_settings_admin_notifications(self):
    return MockRateLimitSettings(), MockOktaResponse(), None

async def get_per_client_rate_limit_settings(self):
    return MockPerClientRateLimit(), MockOktaResponse(), None

async def replace_per_client_rate_limit_settings(self, body):
    return MockPerClientRateLimit(), MockOktaResponse(), None
```

**Tests (~7):** success + error for each of 3 tools; plus update with settings dict.

**Steps:** Same as Task 1. Server.py import after `profile_mappings`, before `roles`.

---

## Task 7: API Tokens Module

**Files:**
- Create: `src/okta_mcp_server/tools/api_tokens/__init__.py`
- Create: `src/okta_mcp_server/tools/api_tokens/api_tokens.py`
- Create: `tests/test_api_tokens.py`
- Modify: `tests/conftest.py`
- Modify: `src/okta_mcp_server/server.py`

**Tools to implement (4):**
1. `list_api_tokens` — `client.list_api_tokens()`, 3-tuple, no params
2. `get_api_token` — `client.get_api_token(token_id)`, 3-tuple
3. `revoke_api_token` — Two-step, `def` (sync), uses "REVOKE" as confirmation word instead of "DELETE"
4. `confirm_revoke_api_token` — `async def`, `client.revoke_api_token(token_id)`, 2-tuple, confirmation must be "REVOKE"

**Key notes:**
- Use "REVOKE" not "DELETE" for the confirmation word (semantically correct for tokens)
- Do NOT create tokens via API — creating SSWS tokens should be done in the Okta admin console for security
- No update — tokens are immutable after creation

**Mock:**
```python
@dataclass
class MockApiToken:
    """Mock Okta API token object."""
    id: str = "tok1abc123"
    name: str = "Test API Token"
    token_window: str = "UNLIMITED"
    created: str = "2024-01-01T00:00:00.000Z"
    last_updated: str = "2024-01-01T00:00:00.000Z"
```

**MockOktaClient methods:**
```python
async def list_api_tokens(self):
    return [MockApiToken()], MockOktaResponse(), None

async def get_api_token(self, token_id):
    return MockApiToken(id=token_id), MockOktaResponse(), None

async def revoke_api_token(self, token_id):
    return None, None
```

**Tests (~10):** success, invalid_id, error for list/get; confirmation + wrong_confirmation + invalid_id + error for revoke flow.

**Steps:** Same as Task 1. Server.py import after `applications`, before `auth_servers`.

---

## Task 8: Update Documentation

**Files:**
- Modify: `README.md` (overview table + 7 new module tables)
- Modify: `CLAUDE.md` (tool table)

**Step 1: Update CLAUDE.md**

Add 7 rows to the tool module table (alphabetical order):

After `applications`:
```
| api_tokens | `tools/api_tokens/api_tokens.py` | API token lifecycle management |
```

After `brands`:
```
| custom_domains | `tools/custom_domains/custom_domains.py` | Custom domain configuration |
```

After `devices`:
```
| email_domains | `tools/email_domains/email_domains.py` | Email sender domain management |
```

After `groups`:
```
| group_rules | `tools/group_rules/group_rules.py` | Dynamic group membership rules |
```

After `inline_hooks`:
```
| linked_objects | `tools/linked_objects/linked_objects.py` | User relationship definitions |
```

After `profile_mappings`:
```
| rate_limits | `tools/rate_limits/rate_limits.py` | API rate limit settings |
```

After `users`:
```
| user_types | `tools/user_types/user_types.py` | Custom user type management |
```

**Step 2: Update README overview table**

Update opening line to say "**228 tools across 31 domains**".

Add to the overview table:

In the **Identity** section:
```
| **Identity** | User Types | 5 | Custom user type management |
```

In the **Security** section:
```
| **Security** | Group Rules | 7 | Dynamic group membership rules |
```

In the **Infrastructure** section:
```
| **Infrastructure** | Custom Domains | 6 | Custom sign-in domain configuration |
| **Infrastructure** | Email Domains | 5 | Email sender domain management |
| **Infrastructure** | Linked Objects | 6 | User relationship definitions |
```

Add new **Governance** section:
```
| **Governance** | API Tokens | 4 | API token lifecycle management |
| **Governance** | Rate Limits | 3 | API rate limit settings |
```

**Step 3: Add 7 module tables to README** (in their respective sections, matching format of existing tables)

**Step 4: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: add Phase 3 modules to README and CLAUDE.md"
```

---

## Task 9: Final Verification

**Step 1: Run full test suite**

```bash
uv run pytest tests/ --tb=short
```

Expected: All tests pass (~660-680 total).

**Step 2: Run lint on all new code**

```bash
uv run ruff check src/okta_mcp_server/tools/group_rules/ src/okta_mcp_server/tools/linked_objects/ src/okta_mcp_server/tools/user_types/ src/okta_mcp_server/tools/custom_domains/ src/okta_mcp_server/tools/email_domains/ src/okta_mcp_server/tools/rate_limits/ src/okta_mcp_server/tools/api_tokens/
```

Expected: All checks pass.

**Step 3: Verify server.py imports**

Read `src/okta_mcp_server/server.py` and confirm all 7 new modules are imported in alphabetical order.

**Step 4: Push**

```bash
git push
```
