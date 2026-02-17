# Code Review Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all 10 prioritized findings from the comprehensive code review of the Okta MCP Server codebase.

**Architecture:** The codebase is a FastMCP server (`server.py`) with 14 tool modules under `src/okta_mcp_server/tools/`, a shared auth manager (`utils/auth/auth_manager.py`), a client factory (`utils/client.py`), and test fixtures in `tests/conftest.py`. All tool functions are registered via `@mcp.tool()` and access the auth manager through MCP context. Tests use `pytest-asyncio` with mock Okta clients.

**Tech Stack:** Python 3.12+, FastMCP, httpx, keyring, PyJWT, okta-sdk-python, pytest, pytest-asyncio, loguru

---

## Task 1: Fix token refresh race condition

**Files:**
- Modify: `src/okta_mcp_server/utils/auth/auth_manager.py:11,31,299`
- Test: `tests/test_auth_manager.py`

When multiple MCP tools fire concurrently and the token is expired, each one calls `is_valid_token()` which triggers `authenticate()`. Without a lock, multiple OAuth flows can run simultaneously, wasting tokens and potentially causing errors.

**Step 1: Write the failing test**

Add to the end of `tests/test_auth_manager.py`:

```python
class TestTokenRefreshRaceCondition:
    """Tests for concurrent token refresh safety."""

    @pytest.mark.asyncio
    async def test_concurrent_is_valid_token_calls_authenticate_once(self, monkeypatch):
        """When multiple calls hit is_valid_token with an expired token, authenticate should only run once."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.get_password", return_value="valid_token"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.token_timestamp = 0  # Expired

            call_count = 0
            original_authenticate = manager.authenticate

            async def counting_authenticate():
                nonlocal call_count
                call_count += 1
                # Simulate auth taking some time
                await asyncio.sleep(0.1)
                manager.token_timestamp = time.time()

            manager.authenticate = counting_authenticate
            manager.refresh_access_token = AsyncMock(return_value=False)

            # Fire 5 concurrent is_valid_token calls
            results = await asyncio.gather(*[manager.is_valid_token() for _ in range(5)])

            # authenticate should have been called exactly once due to the lock
            assert call_count == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth_manager.py::TestTokenRefreshRaceCondition -v`
Expected: FAIL — `call_count` will be 5 because there is no lock.

**Step 3: Write minimal implementation**

In `auth_manager.py`, add `asyncio` import (already present at line 11). Add a lock to the dataclass and use it in `is_valid_token`:

At line 31, inside the `OktaAuthManager` class, add a field after `use_browserless_auth`:

```python
    _token_lock: asyncio.Lock = field(init=False, default_factory=asyncio.Lock)
```

Then wrap the body of `is_valid_token` (lines 299-313) with the lock. Replace the entire method:

```python
    async def is_valid_token(self, expiry_duration: int = 3600) -> bool:
        """Ensure that a valid token is available. Refresh or re-authenticate if needed."""
        async with self._token_lock:
            logger.debug(f"Checking token validity (expiry duration: {expiry_duration}s)")

            api_token = keyring.get_password(SERVICE_NAME, "api_token")
            token_age = time.time() - self.token_timestamp

            if api_token and token_age < expiry_duration:
                logger.debug(f"Token is valid (age: {token_age:.0f}s)")
                return True

            logger.info(f"Token is expired or missing (age: {token_age:.0f}s)")
            if self.use_browserless_auth:
                logger.info("Re-authenticating using browserless flow")
                await self.authenticate()
            else:
                refreshed = await self.refresh_access_token()
                if not refreshed:
                    logger.warning("Token refresh failed, initiating re-authentication")
                    await self.authenticate()

            return keyring.get_password(SERVICE_NAME, "api_token") is not None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_auth_manager.py::TestTokenRefreshRaceCondition -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All 241+ tests pass.

**Step 6: Commit**

```bash
git add src/okta_mcp_server/utils/auth/auth_manager.py tests/test_auth_manager.py
git commit -m "fix: add asyncio.Lock to prevent token refresh race condition"
```

---

## Task 2: Add null check on keyring token in client.py

**Files:**
- Modify: `src/okta_mcp_server/utils/client.py:31`
- Test: `tests/test_auth_manager.py` (add client-focused test)

`keyring.get_password()` can return `None` if the keyring is empty or the entry was deleted. This `None` is then silently passed as `"token": None` to `OktaClient`, which would send `Authorization: Bearer None` in API requests.

**Step 1: Write the failing test**

Create `tests/test_client.py`:

```python
"""Tests for the Okta client factory."""

from unittest.mock import AsyncMock, patch

import pytest


class TestGetOktaClient:
    """Tests for get_okta_client."""

    @pytest.mark.asyncio
    async def test_raises_on_none_token(self, monkeypatch):
        """get_okta_client should raise RuntimeError when keyring returns None."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=True)

            # keyring returns None — token was cleared or never stored
            with patch("okta_mcp_server.utils.client.keyring.get_password", return_value=None):
                from okta_mcp_server.utils.client import get_okta_client

                with pytest.raises(RuntimeError, match="No API token available"):
                    await get_okta_client(manager)

    @pytest.mark.asyncio
    async def test_returns_client_with_valid_token(self, monkeypatch):
        """get_okta_client should return OktaClient when token is available."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with patch("sys.exit"), patch("keyring.set_password"):
            manager = OktaAuthManager()
            manager.is_valid_token = AsyncMock(return_value=True)

            with patch("okta_mcp_server.utils.client.keyring.get_password", return_value="valid_token"):
                from okta_mcp_server.utils.client import get_okta_client

                client = await get_okta_client(manager)
                assert client is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_client.py::TestGetOktaClient::test_raises_on_none_token -v`
Expected: FAIL — no `RuntimeError` is raised, `OktaClient` is created with `None` token.

**Step 3: Write minimal implementation**

In `client.py`, after line 31 (where `api_token` is fetched), add a null check:

```python
    api_token = keyring.get_password(SERVICE_NAME, "api_token")
    if not await manager.is_valid_token():
        logger.warning("Token is invalid or expired, re-authenticating")
        await manager.authenticate()
        api_token = keyring.get_password(SERVICE_NAME, "api_token")
    if not api_token:
        raise RuntimeError("No API token available after authentication. Check keyring configuration.")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_client.py -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass. Some existing tool tests may need the mock to ensure `keyring.get_password` returns a value — check and fix if needed.

**Step 6: Commit**

```bash
git add src/okta_mcp_server/utils/client.py tests/test_client.py
git commit -m "fix: raise RuntimeError when keyring returns None token"
```

---

## Task 3: Replace sys.exit() with exceptions in auth_manager.py

**Files:**
- Modify: `src/okta_mcp_server/utils/auth/auth_manager.py:65,188,284,297`
- Modify: `src/okta_mcp_server/server.py:35` (catch the new exceptions)
- Test: `tests/test_auth_manager.py`

`sys.exit(1)` in async code bypasses the FastMCP lifespan cleanup (token clearing in `server.py:42`). Raising exceptions instead lets the lifespan `finally` block run, and gives callers a chance to handle errors.

**Step 1: Write the failing test**

Add to `tests/test_auth_manager.py`:

```python
class TestAuthManagerExceptions:
    """Tests that auth failures raise exceptions instead of sys.exit."""

    def test_init_missing_env_vars_raises(self, monkeypatch):
        """OktaAuthManager should raise RuntimeError when env vars are missing."""
        monkeypatch.delenv("OKTA_ORG_URL", raising=False)
        monkeypatch.delenv("OKTA_CLIENT_ID", raising=False)

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        with pytest.raises(RuntimeError, match="OKTA_ORG_URL and OKTA_CLIENT_ID must be set"):
            OktaAuthManager()

    @pytest.mark.asyncio
    async def test_device_auth_request_error_raises(self, monkeypatch):
        """Device authorization should raise RuntimeError on request failure."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        import httpx

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )
            with pytest.raises(RuntimeError, match="Failed to initiate device authorization"):
                await manager._initiate_device_authorization()

    @pytest.mark.asyncio
    async def test_browserless_auth_failure_raises(self, monkeypatch):
        """Browserless auth failure should raise RuntimeError."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()
        manager._browserless_authenticate = AsyncMock(return_value=None)

        with pytest.raises(RuntimeError, match="Browserless authentication failed"):
            await manager.authenticate()

    @pytest.mark.asyncio
    async def test_device_flow_auth_failure_raises(self, monkeypatch):
        """Device flow auth failure should raise RuntimeError."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        manager = OktaAuthManager()
        manager._initiate_device_authorization = AsyncMock(return_value={
            "verification_uri_complete": "https://test.okta.com/activate",
            "device_code": "test",
            "interval": 1,
            "expires_in": 1,
            "start_time": 0,
        })
        manager._poll_for_token = AsyncMock(return_value=None)

        with patch("webbrowser.open"):
            with pytest.raises(RuntimeError, match="Authentication failed"):
                await manager.authenticate()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth_manager.py::TestAuthManagerExceptions -v`
Expected: FAIL — `SystemExit` is raised instead of `RuntimeError`.

**Step 3: Write minimal implementation**

Replace all 4 `sys.exit(1)` calls in `auth_manager.py`:

1. **Line 65** (in `__init__`): Replace `sys.exit(1)` with:
   ```python
   raise RuntimeError("OKTA_ORG_URL and OKTA_CLIENT_ID must be set in environment variables")
   ```

2. **Line 188** (in `_initiate_device_authorization`): Replace `sys.exit(1)` with:
   ```python
   raise RuntimeError(f"Failed to initiate device authorization: {e}")
   ```

3. **Line 284** (in `authenticate`, browserless branch): Replace `sys.exit(1)` with:
   ```python
   raise RuntimeError("Browserless authentication failed")
   ```

4. **Line 297** (in `authenticate`, device flow branch): Replace `sys.exit(1)` with:
   ```python
   raise RuntimeError("Authentication failed via device flow")
   ```

Then remove the `import sys` from line 13 (no longer needed after this change). **Wait** — check if `sys` is used elsewhere: `sys.stdout.flush()` at line 223. Keep `import sys`.

Also update `tests/test_auth_manager.py` existing tests: change `with patch("sys.exit"):` to not patch sys.exit since it's no longer called. The existing tests that used `patch("sys.exit")` to suppress the exit in `__init__` now need to ensure the env vars are set (which they already do), so just remove the `patch("sys.exit")` wrappers from:
- `test_init_with_required_env_vars`
- `test_init_adds_https_prefix`
- `test_init_with_browserless_auth`
- `test_init_with_custom_scopes`
- `test_is_valid_token_with_valid_token`
- `test_is_valid_token_with_expired_token`
- `test_refresh_access_token_success`
- `test_refresh_access_token_no_refresh_token`
- `test_clear_tokens`

All of these set the required env vars, so removing `patch("sys.exit")` is safe.

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_auth_manager.py -v`
Expected: PASS for all existing + new tests.

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 6: Commit**

```bash
git add src/okta_mcp_server/utils/auth/auth_manager.py tests/test_auth_manager.py
git commit -m "fix: replace sys.exit() with RuntimeError in auth_manager"
```

---

## Task 4: Remove ctx: Context = None defaults across tool files

**Files to modify** (remove `= None` from `ctx: Context` parameter):
- `src/okta_mcp_server/tools/users/users.py` — lines 118, 155, 184, 222, 257, 291, 324, 358, 392, 426, 460, 494, 530, 572
- `src/okta_mcp_server/tools/groups/groups.py` — lines 107, 140, 177, 204, 244, 360, 395, 429
- `src/okta_mcp_server/tools/brands/brands.py` — lines 78, 427 (these already have `ctx: Context` without `= None` but `ctx` is in the middle of parameters — leave as-is)
- `src/okta_mcp_server/tools/system_logs/system_logs.py` — line 21

This is a mechanical search-and-replace. MCP always provides `ctx`, so the default is misleading and masks bugs if tools are ever called outside the MCP framework.

**Step 1: Run the existing test suite as baseline**

Run: `uv run pytest -v`
Expected: All tests pass (this is a pure signature change; MCP always passes ctx).

**Step 2: Apply the changes**

In each file listed above, change `ctx: Context = None` to `ctx: Context`. This is a find-and-replace operation.

For `users.py`, `groups.py`, `system_logs.py`: every `ctx: Context = None` becomes `ctx: Context`.

**Important edge case:** `users.py:572` has `reset_password(user_id: str, send_email: bool = True, ctx: Context = None)` — `ctx` is the last parameter with a default. Removing the default changes the signature. Since MCP always passes all declared parameters by name, this is safe. Change to `ctx: Context`.

**Step 3: Run the full test suite**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 4: Commit**

```bash
git add src/okta_mcp_server/tools/users/users.py src/okta_mcp_server/tools/groups/groups.py src/okta_mcp_server/tools/system_logs/system_logs.py
git commit -m "fix: remove ctx: Context = None defaults from tool signatures"
```

---

## Task 5: Add JSON decode error handling in auth_manager.py

**Files:**
- Modify: `src/okta_mcp_server/utils/auth/auth_manager.py` — lines 137, 178, 208
- Test: `tests/test_auth_manager.py`

`response.json()` is called without catching `json.JSONDecodeError`. Okta can return HTML error pages during maintenance windows or when a WAF intercepts the request.

**Step 1: Write the failing test**

Add to `tests/test_auth_manager.py`:

```python
import json


class TestJsonDecodeHandling:
    """Tests for JSON decode error handling in auth flows."""

    @pytest.mark.asyncio
    async def test_browserless_auth_handles_html_response(self, monkeypatch):
        """Browserless auth should handle non-JSON responses gracefully."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        mock_response.text = "<html>Error</html>"

        with patch("keyring.set_password"), patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            manager._get_client_assertion = MagicMock(return_value="fake_assertion")

            result = await manager._browserless_authenticate()

        assert result is None

    @pytest.mark.asyncio
    async def test_device_auth_handles_html_response(self, monkeypatch):
        """Device authorization should handle non-JSON responses gracefully."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        mock_response.text = "<html>Error</html>"
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()

            with pytest.raises(RuntimeError, match="Failed to initiate device authorization"):
                await manager._initiate_device_authorization()

    @pytest.mark.asyncio
    async def test_token_poll_handles_html_response(self, monkeypatch):
        """Token polling should handle non-JSON responses gracefully."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        import time

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "<html>", 0)

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()

            device_data = {
                "device_code": "test_code",
                "interval": 0.1,
                "expires_in": 0.5,
                "start_time": time.time(),
            }

            result = await manager._poll_for_token(device_data)

        assert result is None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth_manager.py::TestJsonDecodeHandling -v`
Expected: FAIL — unhandled `json.JSONDecodeError` propagates.

**Step 3: Write minimal implementation**

Wrap `response.json()` calls with try/except in three places:

1. **`_browserless_authenticate`** — line 137, replace:
   ```python
                   resp_json = response.json()
   ```
   with:
   ```python
                   try:
                       resp_json = response.json()
                   except ValueError:
                       logger.error(f"Non-JSON response from token endpoint: {response.text[:200]}")
                       return None
   ```

2. **`_initiate_device_authorization`** — line 178, replace:
   ```python
                 result = response.json()
   ```
   with:
   ```python
                 try:
                     result = response.json()
                 except ValueError as e:
                     logger.error(f"Non-JSON response from device authorization endpoint: {response.text[:200]}")
                     raise RuntimeError(f"Failed to initiate device authorization: {e}")
   ```

3. **`_poll_for_token`** — line 208, replace:
   ```python
                     resp_json = response.json()
   ```
   with:
   ```python
                     try:
                         resp_json = response.json()
                     except ValueError:
                         logger.warning(f"Non-JSON response during token polling: {response.text[:200]}")
                         await asyncio.sleep(device_data["interval"])
                         continue
   ```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_auth_manager.py::TestJsonDecodeHandling -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 6: Commit**

```bash
git add src/okta_mcp_server/utils/auth/auth_manager.py tests/test_auth_manager.py
git commit -m "fix: handle JSON decode errors from Okta API responses"
```

---

## Task 6: Standardize ctx parameter ordering

**Files to modify:**
- `src/okta_mcp_server/tools/users/users.py` — lines 572 (`reset_password`)
- `src/okta_mcp_server/tools/groups/groups.py` — all functions (ctx is last)
- `src/okta_mcp_server/tools/system_logs/system_logs.py` — line 21 (ctx is first but with default)

The codebase has two conventions:
- **Convention A (ctx-first):** `applications.py`, `policies.py`, `authenticators.py`, `auth_servers.py`, `brands.py`, `identity_providers.py`, `network_zones.py`, `trusted_origins.py`, `schemas.py`, `factors.py`, `roles.py`
- **Convention B (ctx-last):** `users.py`, `groups.py`, `system_logs.py`

Convention A (ctx-first) is the majority. Standardize to ctx-first.

**Step 1: Run the existing test suite as baseline**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 2: Apply the changes**

Move `ctx: Context` to be the first parameter in every function that currently has it elsewhere:

**`users.py`** — 14 functions. For each one, move `ctx: Context` from its current position to be the first parameter after `self`/before other params. Example:

```python
# Before:
async def get_user(user_id: str, ctx: Context) -> dict:
# After:
async def get_user(ctx: Context, user_id: str) -> dict:
```

Special case: `list_users` at line ~53 already has ctx... check its signature. It takes `(ctx: Context, ...)` — it's already correct. Only the functions that had `ctx: Context = None` (which we changed to `ctx: Context` in Task 4) need reordering.

Functions to reorder in `users.py`:
- `get_user_profile_attributes(ctx: Context)` — only param, no change needed
- `get_user(user_id: str, ctx: Context)` → `get_user(ctx: Context, user_id: str)`
- `create_user(profile: dict, ctx: Context)` → `create_user(ctx: Context, profile: dict)`
- `update_user(user_id: str, profile: dict, ctx: Context)` → `update_user(ctx: Context, user_id: str, profile: dict)`
- `deactivate_user(user_id: str, ctx: Context)` → `deactivate_user(ctx: Context, user_id: str)`
- `delete_deactivated_user(user_id: str, ctx: Context)` → `delete_deactivated_user(ctx: Context, user_id: str)`
- `activate_user(user_id: str, ctx: Context)` → `activate_user(ctx: Context, user_id: str)`
- `reactivate_user(user_id: str, ctx: Context)` → `reactivate_user(ctx: Context, user_id: str)`
- `suspend_user(user_id: str, ctx: Context)` → `suspend_user(ctx: Context, user_id: str)`
- `unsuspend_user(user_id: str, ctx: Context)` → `unsuspend_user(ctx: Context, user_id: str)`
- `unlock_user(user_id: str, ctx: Context)` → `unlock_user(ctx: Context, user_id: str)`
- `expire_password(user_id: str, ctx: Context)` → `expire_password(ctx: Context, user_id: str)`
- `expire_password_with_temp_password(user_id: str, ctx: Context)` → same pattern
- `reset_password(user_id: str, send_email: bool = True, ctx: Context)` → `reset_password(ctx: Context, user_id: str, send_email: bool = True)`

**`groups.py`** — 8 functions. Same pattern: move `ctx: Context` to first position.
- `get_group(group_id: str, ctx: Context)` → `get_group(ctx: Context, group_id: str)`
- `create_group(profile: dict, ctx: Context)` → `create_group(ctx: Context, profile: dict)`
- `delete_group(group_id: str, ctx: Context)` → `delete_group(ctx: Context, group_id: str)`
- `confirm_delete_group(group_id: str, confirmation: str, ctx: Context)` → `confirm_delete_group(ctx: Context, group_id: str, confirmation: str)`
- `update_group(group_id: str, profile: dict, ctx: Context)` → `update_group(ctx: Context, group_id: str, profile: dict)`
- `list_group_apps(group_id: str, ctx: Context)` → `list_group_apps(ctx: Context, group_id: str)`
- `add_user_to_group(group_id: str, user_id: str, ctx: Context)` → `add_user_to_group(ctx: Context, group_id: str, user_id: str)`
- `remove_user_from_group(group_id: str, user_id: str, ctx: Context)` → `remove_user_from_group(ctx: Context, group_id: str, user_id: str)`

**`system_logs.py`** — `get_logs` already has `ctx` first. No change needed after Task 4.

**Step 3: Run the full test suite**

Run: `uv run pytest -v`
Expected: All tests pass. MCP passes parameters by name, so reordering doesn't affect runtime behavior. Tests also pass parameters by name.

**Step 4: Commit**

```bash
git add src/okta_mcp_server/tools/users/users.py src/okta_mcp_server/tools/groups/groups.py
git commit -m "refactor: standardize ctx as first parameter in all tool functions"
```

---

## Task 7: Wrap keyring.set_password() in try/except

**Files:**
- Modify: `src/okta_mcp_server/utils/auth/auth_manager.py` — lines 142, 213, 218, 262, 266
- Test: `tests/test_auth_manager.py`

In headless environments (Docker, CI), keyring operations can throw `KeyringError`. The `clear_tokens` method already handles this (lines 316-321), but `set_password` calls during token storage don't.

**Step 1: Write the failing test**

Add to `tests/test_auth_manager.py`:

```python
class TestKeyringErrorHandling:
    """Tests for keyring error handling during token storage."""

    @pytest.mark.asyncio
    async def test_browserless_auth_handles_keyring_error(self, monkeypatch):
        """Token storage failure in keyring should not crash browserless auth."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")
        monkeypatch.setenv("OKTA_PRIVATE_KEY", "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----")
        monkeypatch.setenv("OKTA_KEY_ID", "test_key_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("keyring.set_password", side_effect=Exception("No keyring backend")),
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()
            manager._get_client_assertion = MagicMock(return_value="fake_assertion")

            result = await manager._browserless_authenticate()

        # Should still return the token even if keyring storage fails
        assert result == "test_token"

    @pytest.mark.asyncio
    async def test_refresh_handles_keyring_error(self, monkeypatch):
        """Token storage failure in keyring should not crash token refresh."""
        monkeypatch.setenv("OKTA_ORG_URL", "https://test.okta.com")
        monkeypatch.setenv("OKTA_CLIENT_ID", "test_client_id")

        from okta_mcp_server.utils.auth.auth_manager import OktaAuthManager

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new_token", "refresh_token": "new_refresh"}

        call_count = 0

        def failing_set_password(*args):
            nonlocal call_count
            call_count += 1
            raise Exception("No keyring backend")

        with (
            patch("keyring.get_password", return_value="old_refresh_token"),
            patch("keyring.set_password", side_effect=failing_set_password),
            patch("httpx.AsyncClient") as mock_client,
        ):
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            manager = OktaAuthManager()

            result = await manager.refresh_access_token()

        # Should return True — the token was obtained even if storage failed
        assert result is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_auth_manager.py::TestKeyringErrorHandling -v`
Expected: FAIL — unhandled exception propagates from `keyring.set_password`.

**Step 3: Write minimal implementation**

Create a helper method inside `OktaAuthManager` (after `__init__`, around line 72):

```python
    def _store_token(self, key: str, value: str) -> None:
        """Store a token in the keyring, logging errors on failure."""
        try:
            keyring.set_password(SERVICE_NAME, key, value)
        except Exception as e:
            logger.warning(f"Failed to store {key} in keyring: {e}")
```

Then replace all `keyring.set_password(SERVICE_NAME, ...)` calls (lines 142, 213, 218, 262, 266) with `self._store_token(...)`:

- Line 142: `self._store_token("api_token", access_token)`
- Line 213: `self._store_token("api_token", resp_json["access_token"])`
- Line 218: `self._store_token("refresh_token", resp_json["refresh_token"])`
- Line 262: `self._store_token("api_token", resp_json["access_token"])`
- Line 266: `self._store_token("refresh_token", resp_json["refresh_token"])`

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_auth_manager.py::TestKeyringErrorHandling -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 6: Commit**

```bash
git add src/okta_mcp_server/utils/auth/auth_manager.py tests/test_auth_manager.py
git commit -m "fix: wrap keyring.set_password in try/except for headless environments"
```

---

## Task 8: Create test_policies.py and test_system_logs.py

**Files:**
- Create: `tests/test_policies.py`
- Create: `tests/test_system_logs.py`
- Reference: `tests/conftest.py` for mock patterns, `tests/test_applications.py` for structure patterns

These are the only two tool modules with zero test coverage.

**Step 1: Create `tests/test_policies.py`**

Follow the pattern from `test_applications.py`. The policies module has 19 functions. Write tests for the core CRUD operations:

```python
"""Tests for policy management tools."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MockOktaResponse, MockPolicy


class TestListPolicies:
    """Tests for list_policies."""

    @pytest.mark.asyncio
    async def test_list_policies_success(self, mock_context):
        """Test listing policies by type."""
        mock_policy = MockPolicy()
        mock_response = MockOktaResponse()

        mock_client = AsyncMock()
        mock_client.list_policies.return_value = ([mock_policy], mock_response, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON")

        assert "items" in result
        assert result["total_fetched"] >= 0

    @pytest.mark.asyncio
    async def test_list_policies_api_error(self, mock_context):
        """Test list_policies handles API errors."""
        mock_client = AsyncMock()
        mock_client.list_policies.return_value = (None, None, "API Error")

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import list_policies

            result = await list_policies(ctx=mock_context, type="OKTA_SIGN_ON")

        assert result.get("success") is False or "error" in result


class TestGetPolicy:
    """Tests for get_policy."""

    @pytest.mark.asyncio
    async def test_get_policy_success(self, mock_context):
        """Test getting a specific policy."""
        mock_policy = MockPolicy()

        mock_client = AsyncMock()
        mock_client.get_policy.return_value = (mock_policy, None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import get_policy

            result = await get_policy(ctx=mock_context, policy_id="test_policy_id")

        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_get_policy_not_found(self, mock_context):
        """Test getting a policy that doesn't exist."""
        mock_client = AsyncMock()
        mock_client.get_policy.return_value = (None, None, "Not found")

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import get_policy

            result = await get_policy(ctx=mock_context, policy_id="nonexistent")

        assert result.get("success") is False


class TestCreatePolicy:
    """Tests for create_policy."""

    @pytest.mark.asyncio
    async def test_create_policy_success(self, mock_context):
        """Test creating a policy."""
        mock_policy = MockPolicy()

        mock_client = AsyncMock()
        mock_client.create_policy.return_value = (mock_policy, None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import create_policy

            result = await create_policy(
                ctx=mock_context,
                policy_data={"type": "OKTA_SIGN_ON", "name": "Test Policy"},
            )

        assert result.get("success") is True


class TestDeletePolicy:
    """Tests for delete_policy."""

    @pytest.mark.asyncio
    async def test_delete_policy_success(self, mock_context):
        """Test deleting a policy."""
        mock_client = AsyncMock()
        mock_client.delete_policy.return_value = (None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import delete_policy

            result = await delete_policy(ctx=mock_context, policy_id="test_policy_id")

        assert result.get("success") is True


class TestActivateDeactivatePolicy:
    """Tests for activate/deactivate policy."""

    @pytest.mark.asyncio
    async def test_activate_policy_success(self, mock_context):
        """Test activating a policy."""
        mock_client = AsyncMock()
        mock_client.activate_policy.return_value = (None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import activate_policy

            result = await activate_policy(ctx=mock_context, policy_id="test_policy_id")

        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_deactivate_policy_success(self, mock_context):
        """Test deactivating a policy."""
        mock_client = AsyncMock()
        mock_client.deactivate_policy.return_value = (None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import deactivate_policy

            result = await deactivate_policy(ctx=mock_context, policy_id="test_policy_id")

        assert result.get("success") is True


class TestPolicyRules:
    """Tests for policy rule operations."""

    @pytest.mark.asyncio
    async def test_list_policy_rules_success(self, mock_context):
        """Test listing policy rules."""
        mock_client = AsyncMock()
        mock_client.list_policy_rules.return_value = ([], None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import list_policy_rules

            result = await list_policy_rules(ctx=mock_context, policy_id="test_policy_id")

        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_create_policy_rule_success(self, mock_context):
        """Test creating a policy rule."""
        mock_client = AsyncMock()
        mock_client.create_policy_rule.return_value = (MockPolicy(), None, None)

        with patch("okta_mcp_server.tools.policies.policies.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.policies.policies import create_policy_rule

            result = await create_policy_rule(
                ctx=mock_context,
                policy_id="test_policy_id",
                rule_data={"name": "Test Rule", "type": "SIGN_ON"},
            )

        assert result.get("success") is True
```

**Step 2: Create `tests/test_system_logs.py`**

```python
"""Tests for system log retrieval tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import MockOktaResponse


class TestGetLogs:
    """Tests for get_logs."""

    @pytest.mark.asyncio
    async def test_get_logs_success(self, mock_context):
        """Test retrieving system logs."""
        mock_log = MagicMock()
        mock_log.published = "2024-01-01T00:00:00.000Z"
        mock_log.eventType = "user.session.start"
        mock_response = MockOktaResponse()

        mock_client = AsyncMock()
        mock_client.get_logs.return_value = ([mock_log], mock_response, None)

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

        assert "items" in result
        assert result["total_fetched"] == 1

    @pytest.mark.asyncio
    async def test_get_logs_empty(self, mock_context):
        """Test retrieving logs when none exist."""
        mock_response = MockOktaResponse()

        mock_client = AsyncMock()
        mock_client.get_logs.return_value = ([], mock_response, None)

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

        assert result["total_fetched"] == 0

    @pytest.mark.asyncio
    async def test_get_logs_api_error(self, mock_context):
        """Test get_logs handles API errors."""
        mock_client = AsyncMock()
        mock_client.get_logs.return_value = (None, None, "API Error")

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, mock_context):
        """Test get_logs passes filter parameters correctly."""
        mock_response = MockOktaResponse()
        mock_client = AsyncMock()
        mock_client.get_logs.return_value = ([], mock_response, None)

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(
                ctx=mock_context,
                since="2024-01-01T00:00:00.000Z",
                until="2024-01-02T00:00:00.000Z",
                q="login",
                limit=50,
            )

        assert result["total_fetched"] == 0
        # Verify the client was called with query params
        mock_client.get_logs.assert_called_once()
        call_args = mock_client.get_logs.call_args[0][0]
        assert call_args["since"] == "2024-01-01T00:00:00.000Z"
        assert call_args["q"] == "login"

    @pytest.mark.asyncio
    async def test_get_logs_limit_clamping(self, mock_context):
        """Test that limit is clamped to valid range."""
        mock_response = MockOktaResponse()
        mock_client = AsyncMock()
        mock_client.get_logs.return_value = ([], mock_response, None)

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            # Limit below minimum
            await get_logs(ctx=mock_context, limit=5)
            call_args = mock_client.get_logs.call_args[0][0]
            assert call_args["limit"] == "20"

            # Limit above maximum
            await get_logs(ctx=mock_context, limit=500)
            call_args = mock_client.get_logs.call_args[0][0]
            assert call_args["limit"] == "100"

    @pytest.mark.asyncio
    async def test_get_logs_exception_handling(self, mock_context):
        """Test get_logs handles unexpected exceptions."""
        mock_client = AsyncMock()
        mock_client.get_logs.side_effect = Exception("Unexpected error")

        with patch("okta_mcp_server.tools.system_logs.system_logs.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.system_logs.system_logs import get_logs

            result = await get_logs(ctx=mock_context)

        assert result.get("success") is False
        assert "Unexpected error" in result.get("error", "")
```

**Step 3: Run the new tests**

Run: `uv run pytest tests/test_policies.py tests/test_system_logs.py -v`
Expected: PASS

**Step 4: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass.

**Step 5: Commit**

```bash
git add tests/test_policies.py tests/test_system_logs.py
git commit -m "test: add test coverage for policies and system_logs modules"
```

---

## Task 9: Fix mock pagination in conftest.py

**Files:**
- Modify: `tests/conftest.py:264-275`
- Modify: relevant test files that use `fetch_all=True`

`MockOktaResponse.next()` always returns `([], None)`, meaning `fetch_all=True` pagination paths are never actually exercised. The mock should return configurable next-page data.

**Step 1: Write the failing test**

Add a pagination-specific test in `tests/test_users.py` (or a new `tests/test_pagination.py`):

Create `tests/test_pagination.py`:

```python
"""Tests for pagination behavior with fetch_all=True."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MockOktaResponse, MockUser


class TestFetchAllPagination:
    """Tests that fetch_all=True actually traverses pages."""

    @pytest.mark.asyncio
    async def test_list_users_fetch_all_traverses_pages(self, mock_context):
        """list_users with fetch_all=True should return items from all pages."""
        page1_users = [MockUser(), MockUser()]
        page2_users = [MockUser()]

        page2_response = MockOktaResponse(has_next=False)
        page1_response = MockOktaResponse(
            has_next=True,
            next_url="/api/v1/users?after=cursor123",
            next_page_data=(page2_users, page2_response),
        )

        mock_client = AsyncMock()
        mock_client.list_users.return_value = (page1_users, page1_response, None)

        with patch("okta_mcp_server.tools.users.users.get_okta_client", return_value=mock_client):
            from okta_mcp_server.tools.users.users import list_users

            result = await list_users(ctx=mock_context, fetch_all=True)

        assert result["total_fetched"] == 3
        assert result["fetch_all_used"] is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_pagination.py -v`
Expected: FAIL — `total_fetched` is 2 because `next()` returns empty.

**Step 3: Write minimal implementation**

Update `MockOktaResponse` in `conftest.py` to support configurable next-page data:

Replace the `MockOktaResponse` class (lines 264-275):

```python
class MockOktaResponse:
    """Mock Okta API response object."""

    def __init__(self, has_next: bool = False, next_url: Optional[str] = None, next_page_data=None):
        self._has_next = has_next
        self._next = next_url
        self._next_page_data = next_page_data  # Tuple of (items, next_response) or None
        self._next_called = False

    def has_next(self) -> bool:
        if self._next_called:
            return False
        return self._has_next

    async def next(self):
        self._next_called = True
        if self._next_page_data:
            items, next_response = self._next_page_data
            # Update self to behave like the next response for further pagination
            self._has_next = next_response._has_next if next_response else False
            self._next = next_response._next if next_response else None
            self._next_page_data = next_response._next_page_data if next_response else None
            self._next_called = False
            return items, None
        return [], None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_pagination.py -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `uv run pytest -v`
Expected: All existing tests still pass (backward compatible — default `next_page_data=None` preserves old behavior).

**Step 6: Commit**

```bash
git add tests/conftest.py tests/test_pagination.py
git commit -m "fix: make MockOktaResponse support configurable pagination data"
```

---

## Task 10: Replace weak test assertions

**Files:**
- Modify: Various test files

Many tests use assertions like `assert "items" in result or "error" not in result` which always pass because `or` makes them tautological. These need to be replaced with precise assertions.

**Step 1: Find all weak assertions**

Search for patterns like:
- `assert ... or ...` (tautological or)
- `assert "items" in result` without checking values
- `assert result` (truthy check on a dict — always True)

Run: `grep -rn 'assert.*\bor\b' tests/` to find them.

**Step 2: Fix assertions in each file**

The pattern to follow: assert the exact expected structure.

For success cases:
```python
# Before (weak):
assert "items" in result or "error" not in result

# After (precise):
assert result["success"] is True  # or assert "items" in result and result["total_fetched"] >= 0
```

For error cases:
```python
# Before (weak):
assert result

# After (precise):
assert result["success"] is False
assert "error" in result
```

This task requires manual inspection. The subagent should:
1. Read each test file
2. Identify weak assertions
3. Replace with precise ones matching the actual return structure from `success_response()`, `error_response()`, or `create_paginated_response()`

Response structures for reference:
- `success_response(data)` returns `{"success": True, "data": ...}`
- `error_response(error)` returns `{"success": False, "error": "..."}`
- `create_paginated_response(items, response, fetch_all)` returns `{"items": [...], "total_fetched": N, "has_more": bool, "next_cursor": str|None, "fetch_all_used": bool}`

**Step 3: Run full test suite**

Run: `uv run pytest -v`
Expected: All tests pass with the stricter assertions. If any fail, the test was hiding a bug — investigate and fix.

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: replace weak assertions with precise structural checks"
```

---

## Task 11 (Bonus): Commit CLAUDE.md and clean up

**Files:**
- `CLAUDE.md` (already modified, uncommitted from previous session)

**Step 1: Commit CLAUDE.md**

```bash
git add CLAUDE.md
git commit -m "docs: rewrite CLAUDE.md with full tool module coverage"
```

**Step 2: Add .DS_Store to .gitignore**

Check if `.gitignore` exists and add `.DS_Store` if not present:

```bash
echo ".DS_Store" >> .gitignore
git add .gitignore
git commit -m "chore: add .DS_Store to .gitignore"
```

---

## Dependency Graph

```
Task 1 (race condition lock)     ─┐
Task 2 (null token check)        ─┤
Task 3 (sys.exit → exceptions)   ─┤── can run in parallel (independent files/concerns)
Task 5 (JSON decode handling)    ─┤
Task 7 (keyring try/except)      ─┘
         │
         ▼
Task 4 (remove ctx=None)         ─── depends on Task 3 (sys.exit test changes share test file)
         │
         ▼
Task 6 (reorder ctx params)      ─── depends on Task 4 (builds on the same signature changes)
         │
         ▼
Task 8 (new test files)          ─── depends on Tasks 4+6 (needs final function signatures)
         │
         ▼
Task 9 (fix mock pagination)     ─── depends on Task 8 (test files must exist first)
         │
         ▼
Task 10 (fix weak assertions)    ─── depends on Task 9 (all tests must be in final form)
         │
         ▼
Task 11 (commit CLAUDE.md)       ─── run last (clean finish)
```

## Parallel Execution Groups

**Group A (auth_manager.py hardening):** Tasks 1, 3, 5, 7 — all modify `auth_manager.py` but touch different methods. Execute sequentially within group to avoid merge conflicts.

**Group B (client.py):** Task 2 — independent file.

**Group C (tool signatures):** Tasks 4, 6 — sequential, depends on Group A completing.

**Group D (test coverage):** Tasks 8, 9, 10 — sequential, depends on Group C.

**Group E (cleanup):** Task 11 — last.

Recommended subagent dispatch order:
1. Group A (Tasks 1→3→5→7) + Group B (Task 2) in parallel
2. Group C (Tasks 4→6)
3. Group D (Tasks 8→9→10)
4. Group E (Task 11)
