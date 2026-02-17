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
| users | `tools/users/users.py` | User CRUD, deactivation, profile attributes |
| groups | `tools/groups/groups.py` | Group CRUD, membership management |
| applications | `tools/applications/applications.py` | App CRUD, activation/deactivation |
| policies | `tools/policies/policies.py` | Policy and policy rule management |
| system_logs | `tools/system_logs/system_logs.py` | System log retrieval |
| auth_servers | `tools/auth_servers/auth_servers.py` | Authorization server management |
| authenticators | `tools/authenticators/authenticators.py` | Authenticator configuration |
| brands | `tools/brands/brands.py` | Brand/theme management |
| factors | `tools/factors/factors.py` | MFA factor management |
| identity_providers | `tools/identity_providers/identity_providers.py` | IdP configuration |
| network_zones | `tools/network_zones/network_zones.py` | Network zone management |
| roles | `tools/roles/roles.py` | Role-based access management |
| schemas | `tools/schemas/schemas.py` | User/group schema management |
| trusted_origins | `tools/trusted_origins/trusted_origins.py` | CORS trusted origins |

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
2. `tools/groups/groups.py` — Made `delete_group` async for consistency
3. `tools/policies/policies.py` — Fixed pagination cursor extraction using shared `extract_after_cursor` utility
4. `utils/auth/auth_manager.py` — Added `sys.exit(1)` on device flow auth failure
5. `run-server.sh` — Added convenience startup script
