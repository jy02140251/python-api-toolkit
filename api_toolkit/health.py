"""Health check utilities for API services."""

import time
import socket
import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    status: HealthStatus
    version: str
    uptime_seconds: float
    timestamp: str
    components: List[ComponentHealth] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "version": self.version,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "timestamp": self.timestamp,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "latency_ms": round(c.latency_ms, 2),
                    "message": c.message,
                }
                for c in self.components
            ],
        }


class HealthChecker:
    """Configurable health checker with component checks."""

    def __init__(self, service_name: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.version = version
        self._start_time = time.time()
        self._checks: Dict[str, Callable] = {}

    def add_check(self, name: str, check_fn: Callable[[], bool]) -> None:
        self._checks[name] = check_fn

    def check_tcp(self, host: str, port: int, timeout: float = 3.0) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def run_checks(self) -> SystemHealth:
        components = []
        overall_healthy = True

        for name, check_fn in self._checks.items():
            start = time.perf_counter()
            try:
                result = check_fn()
                latency = (time.perf_counter() - start) * 1000
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                if not result:
                    overall_healthy = False
                components.append(ComponentHealth(name=name, status=status, latency_ms=latency))
            except Exception as e:
                latency = (time.perf_counter() - start) * 1000
                overall_healthy = False
                components.append(
                    ComponentHealth(name=name, status=HealthStatus.UNHEALTHY,
                                    latency_ms=latency, message=str(e))
                )

        uptime = time.time() - self._start_time
        return SystemHealth(
            status=HealthStatus.HEALTHY if overall_healthy else HealthStatus.DEGRADED,
            version=self.version,
            uptime_seconds=uptime,
            timestamp=datetime.utcnow().isoformat(),
            components=components,
        )