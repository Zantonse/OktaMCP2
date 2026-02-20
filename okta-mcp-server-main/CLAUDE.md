# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Okta MCP Server**, a Model Context Protocol server that allows LLM agents to manage Okta organizations via natural language. It integrates with Okta's Admin Management APIs through the official Okta Python SDK. Beta software, Apache 2.0 licensed.

## Commands

### Install and Run
```bash
uv sync                    # Install dependencies
uv run okta-mcp-server     # Run the server
./run-server.sh            # Run with .env file auto-loaded
```

### Linting
```bash
uv run ruff check .        # Check for lint errors
uv run ruff check --fix .  # Auto-fix lint errors
uv run ruff format .       # Format code
```

### Testing
```bash
uv run pytest                          # Run all tests
uv run pytest tests/test_users.py      # Run specific test file
uv run pytest -k "test_name"           # Run tests matching pattern
```

### Debug Mode
```bash
export OKTA_LOG_LEVEL=DEBUG
export OKTA_LOG_FILE="/path/to/okta-mcp.log"  # Optional file output
```

## Architecture

### Entry Point & Server Lifecycle
`src/okta_mcp_server/__init__.py` → `server.py:main()` → initializes logger, lazy-imports all tool modules, calls `mcp.run()`.

The `FastMCP` instance is created at module level in `server.py` with a lifespan context manager (`okta_authorisation_flow`) that handles authentication on startup and token cleanup on shutdown. The lifespan yields an `OktaAppContext` dataclass containing the `OktaAuthManager` instance.

### Tool Modules
All tools live under `src/okta_mcp_server/tools/`, organized by Okta resource domain:

| Module | Path | Purpose |
|--------|------|---------|
| api_tokens | `tools/api_tokens/api_tokens.py` | API token lifecycle management |
| applications | `tools/applications/applications.py` | App CRUD, user/group assignment |
| auth_servers | `tools/auth_servers/auth_servers.py` | Authorization server management |
| authenticators | `tools/authenticators/authenticators.py` | Authenticator configuration |
| behaviors | `tools/behaviors/behaviors.py` | Behavior detection rule management |
| brands | `tools/brands/brands.py` | Brand/theme management |
| custom_domains | `tools/custom_domains/custom_domains.py` | Custom domain configuration |
| devices | `tools/devices/devices.py` | Device management |
| device_assurance | `tools/device_assurance/device_assurance.py` | Device assurance policy management |
| email_domains | `tools/email_domains/email_domains.py` | Email sender domain management |
| event_hooks | `tools/event_hooks/event_hooks.py` | Event hook management |
| features | `tools/features/features.py` | Org feature flag management |
| factors | `tools/factors/factors.py` | MFA factor management |
| group_rules | `tools/group_rules/group_rules.py` | Dynamic group membership rules |
| groups | `tools/groups/groups.py` | Group CRUD, membership management |
| identity_providers | `tools/identity_providers/identity_providers.py` | IdP configuration |
| inline_hooks | `tools/inline_hooks/inline_hooks.py` | Inline hook management |
| linked_objects | `tools/linked_objects/linked_objects.py` | User relationship definitions |
| network_zones | `tools/network_zones/network_zones.py` | Network zone management |
| org_settings | `tools/org_settings/org_settings.py` | Organization settings |
| policies | `tools/policies/policies.py` | Policy and policy rule management |
| profile_mappings | `tools/profile_mappings/profile_mappings.py` | Profile attribute mappings |
| rate_limits | `tools/rate_limits/rate_limits.py` | API rate limit settings |
| roles | `tools/roles/roles.py` | Role-based access management |
| schemas | `tools/schemas/schemas.py` | User/group schema management |
| sessions | `tools/sessions/sessions.py` | Session management |
| system_logs | `tools/system_logs/system_logs.py` | System log retrieval |
| threat_insight | `tools/threat_insight/threat_insight.py` | ThreatInsight configuration |
| trusted_origins | `tools/trusted_origins/trusted_origins.py` | CORS trusted origins |
| user_types | `tools/user_types/user_types.py` | Custom user type management |
| users | `tools/users/users.py` | User CRUD, lifecycle, profile attributes |

### Tool Registration Pattern
Every tool function follows this pattern — access the auth manager from context, create an authenticated client, make the API call, return a standardized response:
```python
from okta_mcp_server.server import mcp
from okta_mcp_server.utils.client import get_okta_client

@mcp.tool()
async def some_tool(ctx: Context, ...) -> dict:
    manager = ctx.request_context.lifespan_context.okta_auth_manager
    client = await get_okta_client(manager)
    # ... Okta SDK calls ...
    return success_response(data)
```

### Authentication
`utils/auth/auth_manager.py` — `OktaAuthManager` class supports two flows:
- **Device Authorization Grant** — Interactive browser-based flow (default)
- **Private Key JWT** — Browserless client credentials flow (when `OKTA_PRIVATE_KEY` and `OKTA_KEY_ID` are set)

Tokens stored in system keyring under service name `OktaAuthManager`.

### Utilities
- `utils/client.py` — Creates authenticated `OktaClient` instances with automatic token refresh and retry (3 attempts, exponential backoff)
- `utils/pagination.py` — `extract_after_cursor()` parses Okta's `_next` URL, `paginate_all_results()` auto-pages through responses, `create_paginated_response()` builds standardized paginated output, `build_query_params()` constructs API query dicts
- `utils/response.py` — `ToolResponse` and `PaginatedResponse` dataclasses with `to_dict()`. Helper functions: `success_response(data)` and `error_response(error)`
- `utils/retry.py` — `@with_retry` decorator using tenacity for exponential backoff on transient failures
- `utils/validators.py` — Input validation for emails, Okta IDs, timestamps

### Test Infrastructure
Tests use pytest-asyncio. `tests/conftest.py` provides mock fixtures for all major Okta objects (MockUser, MockGroup, MockAuthorizationServer, MockPolicy, etc.) and pre-configured auth manager mocks.

## Code Conventions

### Ruff Configuration (`.ruff.toml`)
- Line length: 119 characters
- Quote style: double quotes
- Rules: Pyflakes (F), pycodestyle (E), isort (I), Ruff-specific (RUF)

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

## Input Validation & Error Handling Patterns

- All tool functions validate ID parameters with `validate_okta_id()` before making API calls
- All tool functions use `validate_limit()` for limit parameter clamping instead of inline logic
- All error responses use `sanitize_error()` to strip sensitive data (Okta URLs, tokens) before returning to MCP clients
- `ctx: Context` is always the first parameter in tool function signatures
- Exception handling: bare `except Exception` is used as a final catch-all, but API errors from Okta SDK (returned as `err` from tuple unpacking) are handled first

### Deletion Safety Pattern
Destructive operations (delete_user, delete_group, delete_application) use a two-step confirmation:
1. First call returns `{"confirmation_required": True, "message": "..."}`
2. User must explicitly confirm
3. Second call (`confirm_delete_*`) executes the deletion

### Environment Variables
- `OKTA_ORG_URL` (required) — Okta organization URL
- `OKTA_CLIENT_ID` (required) — OAuth client ID
- `OKTA_SCOPES` — Space-separated OAuth scopes
- `OKTA_PRIVATE_KEY` — RSA private key for browserless auth
- `OKTA_KEY_ID` — Key ID for browserless auth
- `OKTA_LOG_LEVEL` — Log level (default: INFO)
- `OKTA_LOG_FILE` — Optional log file path

## Local Modifications
This fork has local changes tracked in `changes.md`:
1. `__init__.py` — Removed `asyncio.run()` wrapper (FastMCP handles async internally)
2. `tools/groups/groups.py` — Changed `delete_group` to sync `def` (two-step deletion pattern)
3. `tools/policies/policies.py` — Fixed pagination cursor extraction using shared `extract_after_cursor` utility
4. `utils/auth/auth_manager.py` — Added `sys.exit(1)` on device flow auth failure
5. `run-server.sh` — Added convenience startup script
