# Full Code Review Fixes — Design Document

**Date:** 2026-02-17
**Approach:** Bottom-Up (Utilities First, Then Tools)

## Problem Statement

A comprehensive code review identified 139 bare `except Exception` handlers, duplicate limit-validation logic across 12 list functions, missing input validation in all 14 tool modules, a token refresh race condition, incomplete utility test coverage, and inconsistent error/response formats. This design addresses all findings.

## Phase 1: Utility Infrastructure Fixes

### 1a. validators.py

Add two new functions:

- **`validate_limit(limit, min_val=20, max_val=100)`** — Clamp limit to valid range, log warnings. Returns clamped value. Replaces the 12 duplicate blocks across tool modules.
- **`sanitize_error(error)`** — Strip sensitive Okta API details (URLs, tokens, internal IDs) from error messages before returning to clients. Returns a safe string.

### 1b. retry.py

- Expand `RETRYABLE_EXCEPTIONS` to include `httpx.TimeoutException`, `httpx.ConnectError`, `httpx.HTTPStatusError` (for 5xx only).
- Ensure `retry_on_rate_limit()` is functional and tested — it exists but is currently unused.

### 1c. auth_manager.py

- **Race condition fix:** Add a `_refresh_lock` asyncio.Lock that wraps the entire token refresh flow. When multiple tools detect an expired token concurrently, only the first caller refreshes; subsequent callers wait on the lock and then re-check token validity before attempting their own refresh.
- **Private key validation:** On startup, validate that `OKTA_PRIVATE_KEY` is a parseable RSA key using `jwt.algorithms.RSAAlgorithm.from_jwk()` or `cryptography` — fail fast with a clear error.
- **Configurable HTTP timeout:** Read `OKTA_HTTP_TIMEOUT` env var (default 30s).
- **Keyring resilience:** If keyring is unavailable, log a warning and fall back to in-memory token storage instead of silently continuing with no storage.

### 1d. client.py

- Apply `retry_on_rate_limit()` decorator to `get_okta_client()`.
- After token refresh, validate the token is not None before proceeding.
- Return a clear error if client creation fails.

### 1e. pagination.py

- Validate `response` has expected attributes before accessing them.
- Accept optional `delay` parameter (default 0.1s).
- When a pagination page fails, include a warning in the response metadata rather than silently returning partial results.

## Phase 2: Tool Module Fixes (All 14 Modules)

Apply these changes to every tool file:

1. **Replace `except Exception` with specific exceptions:** Use `OktaAPIError` (from SDK), `httpx.HTTPError`, `ValueError`, `KeyError` as appropriate. Keep a final `except Exception` only as a last-resort catch-all that logs at ERROR level with traceback.
2. **Replace duplicate limit validation** with `validators.validate_limit(limit)`.
3. **Add input validation** using existing validators: `validate_email()` for user creation, `validate_okta_id()` for ID parameters, `validate_required_string()` for required fields.
4. **Sanitize error messages** using `validators.sanitize_error(str(err))` before passing to `error_response()`.
5. **Standardize return formats** — ensure all list operations return consistent structures (list of dicts, not mixed tuples/objects).

### Affected modules (14 total):
- users.py, groups.py, applications.py, policies.py, system_logs.py
- auth_servers.py, authenticators.py, brands.py, factors.py
- identity_providers.py, network_zones.py, roles.py, schemas.py, trusted_origins.py

## Phase 3: Missing Test Coverage

### New test files:
- **test_response.py** — ToolResponse/PaginatedResponse dataclasses, success_response(), error_response(), to_dict() serialization.
- **test_client.py** — get_okta_client() happy path, token refresh failure, retry on transient error, rate limit handling.
- **test_retry.py** — with_retry decorator (success, retryable failure, non-retryable failure, max attempts), retry_on_rate_limit() (429 handling, backoff).

### Expanded test files:
- **test_server.py** — Lifespan context manager, tool module import failure handling, logger configuration.
- **test_auth_manager.py** — Concurrent token refresh (race condition), keyring failure fallback, private key validation failure.

## Phase 4: Configuration & Documentation

- **pyproject.toml:** Remove duplicate dependency group, add `[tool.pytest.ini_options]` section.
- **CLAUDE.md:** Update with new patterns (validate_limit, sanitize_error, specific exceptions).
- **CHANGELOG.md:** Add entry for this review's changes.

## Out of Scope

- Connection pooling for httpx (optimization, not correctness)
- Pagination result caching (would need cache invalidation strategy)
- Okta API response schema validation (would need schema definitions from Okta)
- New tool modules or features

## Success Criteria

- Zero bare `except Exception` handlers without justification
- All 14 tool modules use validators for input validation
- All utility modules have test coverage
- Token refresh race condition eliminated
- All existing tests still pass after changes
