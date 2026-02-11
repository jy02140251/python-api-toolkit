"""Tests for health check utilities."""

import pytest
from api_toolkit.health import HealthChecker, HealthStatus, SystemHealth


class TestHealthChecker:
    def test_basic_initialization(self):
        checker = HealthChecker("test-service", "2.0.0")
        assert checker.service_name == "test-service"
        assert checker.version == "2.0.0"

    def test_all_checks_healthy(self):
        checker = HealthChecker("test")
        checker.add_check("db", lambda: True)
        checker.add_check("cache", lambda: True)
        result = checker.run_checks()
        assert result.status == HealthStatus.HEALTHY
        assert len(result.components) == 2

    def test_one_check_unhealthy(self):
        checker = HealthChecker("test")
        checker.add_check("db", lambda: True)
        checker.add_check("cache", lambda: False)
        result = checker.run_checks()
        assert result.status == HealthStatus.DEGRADED

    def test_check_with_exception(self):
        def failing_check():
            raise ConnectionError("Cannot connect")
        checker = HealthChecker("test")
        checker.add_check("db", failing_check)
        result = checker.run_checks()
        assert result.status == HealthStatus.DEGRADED
        assert result.components[0].message == "Cannot connect"

    def test_to_dict_format(self):
        checker = HealthChecker("test", "1.0.0")
        checker.add_check("ping", lambda: True)
        result = checker.run_checks()
        d = result.to_dict()
        assert d["status"] == "healthy"
        assert d["version"] == "1.0.0"
        assert "uptime_seconds" in d
        assert "components" in d

    def test_tcp_check_invalid_host(self):
        checker = HealthChecker("test")
        assert checker.check_tcp("invalid-host-xyz", 9999, timeout=0.5) is False