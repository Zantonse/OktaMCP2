# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

"""Retry utilities for handling transient failures in Okta API calls."""

from functools import wraps
from typing import Callable, TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")

# Default retry configuration
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MIN_WAIT = 1  # seconds
DEFAULT_MAX_WAIT = 10  # seconds

# Exceptions that should trigger a retry
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def with_retry(
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    min_wait: float = DEFAULT_MIN_WAIT,
    max_wait: float = DEFAULT_MAX_WAIT,
    retryable_exceptions: tuple = RETRYABLE_EXCEPTIONS,
) -> Callable:
    """Decorator that adds retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        retryable_exceptions: Tuple of exception types that should trigger retries

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(min=min_wait, max=max_wait),
            retry=retry_if_exception_type(retryable_exceptions),
            reraise=True,
        )
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            return await func(*args, **kwargs)

        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(min=min_wait, max=max_wait),
            retry=retry_if_exception_type(retryable_exceptions),
            reraise=True,
        )
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def retry_on_rate_limit(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator specifically for handling Okta rate limit errors (429).

    Implements longer backoff for rate limit scenarios.
    """
    return with_retry(
        max_attempts=5,
        min_wait=2,
        max_wait=30,
    )(func)


class RetryableError(Exception):
    """Custom exception to indicate an error that should be retried."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error
