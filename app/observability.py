"""Centralized logging and observability utilities for the application."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional, Protocol

import psutil


class ProcessLike(Protocol):
    """Protocol for process-like objects (for testability)."""

    def memory_info(self):
        """Return process memory information."""

    def cpu_percent(self, interval: float):
        """Return process CPU usage percentage."""


@dataclass(frozen=True)
class ObservabilityConfig:
    """Runtime configuration for observability features."""

    resource_logging_enabled: bool = True


class Observability:
    """Observability and resource logging manager."""

    def __init__(
        self,
        *,
        config: ObservabilityConfig,
        process: Optional[ProcessLike] = None,
    ) -> None:
        self._config = config
        self._process = process

    @classmethod
    def setup(
        cls,
        *,
        level: int = logging.INFO,
        enable_resource_logging: bool = True,
    ) -> "Observability":
        """Configure logging and create an Observability instance.

        Intended to be called once at application startup.
        """

        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )

        process = psutil.Process(os.getpid())

        obs = cls(
            config=ObservabilityConfig(
                resource_logging_enabled=enable_resource_logging
            ),
            process=process,
        )

        _set_default_observability(obs)
        return obs

    def get_logger(self, name: str) -> logging.Logger:
        """Return a module-scoped logger."""
        return logging.getLogger(name)

    def log_resources(self, label: str = "") -> None:
        """Log current process memory and CPU usage."""

        if not self._config.resource_logging_enabled:
            return

        if self._process is None:
            return

        mem_mb = self._process.memory_info().rss / 1024 / 1024
        cpu_pct = self._process.cpu_percent(interval=0.1)

        logger = logging.getLogger("observability.resources")

        logger.info(
            "Resource usage | context=%s | memory_mb=%.1f | cpu_pct=%.1f",
            label,
            mem_mb,
            cpu_pct,
        )


# Runtime default observability instance (mutable by design)
_default_observability: Optional[Observability] = None  # pylint: disable=invalid-name


def _set_default_observability(obs: Observability) -> None:
    """Set the default observability context (internal)."""
    global _default_observability  # pylint: disable=global-statement
    _default_observability = obs


def _reset_default_observability() -> None:
    """Reset default observability (for tests only)."""
    global _default_observability  # pylint: disable=global-statement
    _default_observability = None


def get_logger(name: str) -> logging.Logger:
    """Backward-compatible logger accessor.

    Prefer using `Observability.get_logger()` in new code.
    """
    if _default_observability is not None:
        return _default_observability.get_logger(name)

    return logging.getLogger(name)


def log_resources(label: str = "") -> None:
    """Backward-compatible resource logger.

    No-op if observability has not been set up.
    """
    if _default_observability is None:
        return

    _default_observability.log_resources(label)
