"""Tests for the Retry module."""

import pytest
from api_toolkit.retry import retry


class TestRetry:
    """Tests for retry decorator."""

    def test_success_no_retry(self):
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        def succeeds():
            nonlocal call_count
            call_count += 1
            return "ok"

        assert succeeds() == "ok"
        assert call_count == 1

    def test_retries_on_failure(self):
        call_count = 0

        @retry(max_attempts=3, initial_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("fail")
            return "ok"

        assert fails_twice() == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self):
        @retry(max_attempts=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("permanent error")

        with pytest.raises(ValueError, match="permanent error"):
            always_fails()

    def test_only_retries_specified_exceptions(self):
        @retry(
            max_attempts=3,
            initial_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        def raises_value_error():
            raise ValueError("not retryable")

        with pytest.raises(ValueError):
            raises_value_error()