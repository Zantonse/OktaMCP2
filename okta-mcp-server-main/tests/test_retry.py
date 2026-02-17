"""Tests for retry utilities."""

import pytest

from okta_mcp_server.utils.retry import RetryableError, retry_on_rate_limit, with_retry


class TestWithRetry:
    """Tests for with_retry decorator."""

    @pytest.mark.asyncio
    async def test_async_function_succeeds_first_try(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await succeed()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_retries_on_connection_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("connection refused")
            return "ok"

        result = await fail_then_succeed()
        assert result == "ok"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_async_retries_on_timeout_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def timeout_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("timed out")
            return "ok"

        result = await timeout_then_succeed()
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_async_retries_on_os_error(self):
        call_count = 0

        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        async def os_error_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("network unreachable")
            return "ok"

        result = await os_error_then_succeed()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_async_raises_after_max_attempts(self):
        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        async def always_fail():
            raise ConnectionError("connection refused")

        with pytest.raises(ConnectionError, match="connection refused"):
            await always_fail()

    @pytest.mark.asyncio
    async def test_async_non_retryable_raises_immediately(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        async def raise_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("bad value")

        with pytest.raises(ValueError):
            await raise_value_error()
        assert call_count == 1

    def test_sync_function_succeeds(self):
        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def succeed():
            return "ok"

        assert succeed() == "ok"

    def test_sync_retries_on_connection_error(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("refused")
            return "ok"

        result = fail_then_succeed()
        assert result == "ok"
        assert call_count == 3

    def test_sync_raises_after_max_attempts(self):
        @with_retry(max_attempts=2, min_wait=0, max_wait=0)
        def always_fail():
            raise ConnectionError("refused")

        with pytest.raises(ConnectionError):
            always_fail()

    def test_sync_non_retryable_raises_immediately(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0)
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("bad type")

        with pytest.raises(TypeError):
            raise_type_error()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_custom_retryable_exceptions(self):
        call_count = 0

        @with_retry(max_attempts=3, min_wait=0, max_wait=0, retryable_exceptions=(ValueError,))
        async def custom_retry():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("retryable")
            return "ok"

        result = await custom_retry()
        assert result == "ok"
        assert call_count == 2


class TestRetryOnRateLimit:
    """Tests for retry_on_rate_limit decorator."""

    @pytest.mark.asyncio
    async def test_decorates_async_function(self):
        @retry_on_rate_limit
        async def api_call():
            return "result"

        result = await api_call()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_retries_on_connection_error(self):
        call_count = 0

        @retry_on_rate_limit
        async def flaky_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("rate limited")
            return "ok"

        result = await flaky_call()
        assert result == "ok"
        assert call_count == 2


class TestRetryableError:
    """Tests for RetryableError exception."""

    def test_message(self):
        err = RetryableError("something failed")
        assert str(err) == "something failed"

    def test_original_error(self):
        original = ConnectionError("conn refused")
        err = RetryableError("wrapper", original_error=original)
        assert err.original_error is original

    def test_default_original_error_is_none(self):
        err = RetryableError("test")
        assert err.original_error is None

    def test_is_exception(self):
        with pytest.raises(RetryableError):
            raise RetryableError("test")
