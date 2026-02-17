# Full Code Review & Implementation Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all findings from the comprehensive code review — security issues, code quality, missing validation, inconsistent patterns, and test coverage gaps across the entire Okta MCP Server.

**Approach:** Bottom-Up (Utilities first, then Tools, then Tests). Fix shared infrastructure so tool module changes become simpler.

**Architecture:** FastMCP server (`server.py`) with 14 tool modules under `src/okta_mcp_server/tools/`, shared auth manager (`utils/auth/auth_manager.py`), client factory (`utils/client.py`), and utilities (pagination, response, retry, validators). Tests use `pytest-asyncio` with mock Okta clients in `tests/conftest.py`.

**Tech Stack:** Python 3.12+, FastMCP, httpx, keyring, PyJWT, okta-sdk-python, pytest, pytest-asyncio, loguru

---

## Review Summary

| Severity | Category | Count |
|----------|----------|-------|
| Critical | Token refresh race condition | 1 |
| Critical | Bare `except Exception` handlers | ~139 |
| High | Duplicate limit validation logic | ~12 functions |
| High | Missing input validation in tools | 14 modules |
| High | Error messages may expose internals | ~50 instances |
| High | Missing utility test coverage | 4 files |
| Medium | Inconsistent ctx parameter ordering | 3 modules |
| Medium | `ctx: Context = None` defaults | 3 modules |
| Medium | No rate limit handling | unused decorator exists |
| Medium | Keyring errors unhandled in token storage | 5 call sites |
| Medium | No JSON decode error handling in auth | 3 call sites |
| Low | sys.exit() instead of exceptions | 4 call sites |
| Low | Weak test assertions | scattered |
| Low | pyproject.toml duplicate deps | 1 |

---

## Phase 1: Utility Infrastructure Fixes

### Task 1: Fix token refresh race condition in auth_manager.py

**Files:** `src/okta_mcp_server/utils/auth/auth_manager.py`, `tests/test_auth_manager.py`

Add `asyncio.Lock` to `OktaAuthManager` so concurrent `is_valid_token()` calls only trigger one auth flow. The lock wraps the entire validity-check-and-refresh block.

### Task 2: Replace sys.exit() with RuntimeError in auth_manager.py

**Files:** `src/okta_mcp_server/utils/auth/auth_manager.py`, `tests/test_auth_manager.py`

Replace 4 `sys.exit(1)` calls with `raise RuntimeError(...)`. This lets FastMCP lifespan cleanup run properly and makes failures testable. Update existing tests to remove `patch("sys.exit")` wrappers.

### Task 3: Add JSON decode error handling in auth_manager.py

**Files:** `src/okta_mcp_server/utils/auth/auth_manager.py`, `tests/test_auth_manager.py`

Wrap 3 `response.json()` calls in try/except for `ValueError`. Okta can return HTML during maintenance. Each flow handles it differently: browserless returns None, device auth raises RuntimeError, token poll retries.

### Task 4: Wrap keyring.set_password() in try/except

**Files:** `src/okta_mcp_server/utils/auth/auth_manager.py`, `tests/test_auth_manager.py`

Create `_store_token()` helper that wraps `keyring.set_password()` with try/except. Replace 5 direct calls. Handles headless environments (Docker, CI) where keyring is unavailable.

### Task 5: Add null token check in client.py

**Files:** `src/okta_mcp_server/utils/client.py`, `tests/test_client.py` (new)

After `keyring.get_password()`, check for None and raise `RuntimeError` instead of passing `None` token to OktaClient. Write test file for client.py.

### Task 6: Add validate_limit() to validators.py

**Files:** `src/okta_mcp_server/utils/validators.py`, `tests/test_validators.py`

Add `validate_limit(limit, min_val=20, max_val=100)` function that clamps and logs. Also add `sanitize_error(error)` to strip sensitive API details. Write tests for both.

### Task 7: Expand retryable exceptions in retry.py and add rate limit support

**Files:** `src/okta_mcp_server/utils/retry.py`, `tests/test_retry.py` (new)

Add `httpx.TimeoutException` and `httpx.ConnectError` to retryable exceptions. Wire `retry_on_rate_limit()` into client.py. Write test file for retry.py.

---

## Phase 2: Tool Module Fixes (All 14 Modules)

### Task 8: Replace bare `except Exception` with specific exceptions

**Files:** All 14 tool modules under `src/okta_mcp_server/tools/`

Replace `except Exception as e` with specific catches: `except (OktaAPIException, httpx.HTTPError) as e` for API calls, `except ValueError as e` for validation, with a final `except Exception as e` only for truly unexpected errors. Each tool module already imports the client — add the exception imports.

### Task 9: Replace duplicate limit validation with validate_limit()

**Files:** All 14 tool modules that have list functions

Replace the ~12 inline limit-clamping blocks with `validate_limit()` from validators.py.

### Task 10: Add input validation to tool functions

**Files:** All 14 tool modules

Use existing validators (`validate_email`, `validate_okta_id`, `validate_required_string`) at the start of tool functions that accept user input. Specifically:
- `create_user`: validate email format
- Any function taking `*_id`: validate Okta ID format
- Any function taking required strings: validate non-empty

### Task 11: Sanitize error messages in tool responses

**Files:** All 14 tool modules

Replace `error_response(str(err))` with `error_response(sanitize_error(err))` to prevent leaking Okta API internals.

### Task 12: Standardize ctx parameter ordering and remove defaults

**Files:** `users.py`, `groups.py`, `system_logs.py`

Move `ctx: Context` to first parameter position (matching the 11 other modules). Remove `= None` defaults.

---

## Phase 3: Test Coverage

### Task 13: Write test_response.py

**Files:** `tests/test_response.py` (new)

Test `ToolResponse` and `PaginatedResponse` dataclasses, `success_response()`, `error_response()`, `to_dict()` methods.

### Task 14: Write test_retry.py

**Files:** `tests/test_retry.py` (new)

Test `with_retry` decorator with various exception types, max attempts, backoff behavior. Test `retry_on_rate_limit()`.

### Task 15: Write test_server.py (expand)

**Files:** `tests/test_server.py`

Expand existing tests to cover lifespan context manager, tool module imports, logger configuration with invalid paths.

### Task 16: Fix MockOktaResponse pagination support

**Files:** `tests/conftest.py`

Update `MockOktaResponse` to support configurable next-page data so `fetch_all=True` paths are actually tested.

### Task 17: Fix weak test assertions

**Files:** Various test files

Replace tautological `assert ... or ...` and `assert result` with precise structural checks against `success_response`/`error_response`/`create_paginated_response` return formats.

---

## Phase 4: Configuration & Documentation

### Task 18: Fix pyproject.toml

Remove duplicate dependency group. Add `[tool.pytest.ini_options]` section.

### Task 19: Update CLAUDE.md

Document new patterns (validate_limit, sanitize_error, specific exceptions, ctx-first convention).

### Task 20: Update CHANGELOG.md

Add entry for this review's changes.

---

## Execution Order

```
Phase 1 (sequential, shared files):
  Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7

Phase 2 (can parallelize across modules):
  Task 8 + Task 9 + Task 10 + Task 11 (applied together per module)
  Task 12 (separate, simpler)

Phase 3 (after Phase 2 stabilizes signatures):
  Task 13 + Task 14 (parallel, independent files)
  Task 15 → Task 16 → Task 17 (sequential)

Phase 4 (last):
  Task 18 + Task 19 + Task 20
```

Each task follows TDD: write failing test → implement fix → verify pass → run full suite → commit.
