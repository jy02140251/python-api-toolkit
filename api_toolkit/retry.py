"""
Retry Module.

Provides a configurable retry decorator with exponential backoff,
jitter, and customizable exception handling.
"""

import time
import random
import functools
import logging
from dataclasses import dataclass
from typing import Tuple, Type, Callable, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Retry decorator with exponential backoff.

    Automatically retries a function on failure with configurable
    backoff timing and exception filtering.

    Args:
        max_attempts: Maximum number of retry attempts.
        backoff_factor: Multiplier for delay between retries.
        initial_delay: Initial delay in seconds before first retry.
        max_delay: Maximum delay cap in seconds.
        jitter: Whether to add random jitter to delays.
        retryable_exceptions: Tuple of exception types to retry on.
        on_retry: Optional callback invoked on each retry.

    Example:
        >>> @retry(max_attempts=3, backoff_factor=2.0)
        ... def fetch_data():
        ...     return requests.get("https://api.example.com/data")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            "Function %s failed after %d attempts: %s",
                            func.__name__,
                            max_attempts,
                            str(e),
                        )
                        raise

                    # Calculate delay with optional jitter
                    actual_delay = min(delay, max_delay)
                    if jitter:
                        actual_delay *= (0.5 + random.random())

                    logger.warning(
                        "Function %s attempt %d/%d failed: %s. "
                        "Retrying in %.2fs...",
                        func.__name__,
                        attempt,
                        max_attempts,
                        str(e),
                        actual_delay,
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(actual_delay)
                    delay *= backoff_factor

            raise last_exception  # type: ignore

        # Attach config metadata
        wrapper.retry_config = RetryConfig(
            max_attempts=max_attempts,
            backoff_factor=backoff_factor,
            initial_delay=initial_delay,
            max_delay=max_delay,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
        )
        return wrapper

    return decorator