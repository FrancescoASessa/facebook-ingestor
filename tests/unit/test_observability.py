class FakeProcess:
    def memory_info(self):
        class Mem:
            rss = 150 * 1024 * 1024  # 150 MB

        return Mem()

    def cpu_percent(self, interval: float):
        return 37.5


import logging

import pytest

from app.observability import (
    Observability,
    ObservabilityConfig,
    get_logger,
    log_resources,
)


def test_get_logger_returns_logger():
    obs = Observability(
        config=ObservabilityConfig(resource_logging_enabled=True),
        process=None,
    )

    logger = obs.get_logger("test.module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_log_resources_disabled_no_log(caplog):
    obs = Observability(
        config=ObservabilityConfig(resource_logging_enabled=False),
        process=FakeProcess(),
    )

    with caplog.at_level("INFO"):
        obs.log_resources("test")

    assert caplog.text == ""


def test_log_resources_no_process_no_crash(caplog):
    obs = Observability(
        config=ObservabilityConfig(resource_logging_enabled=True),
        process=None,
    )

    with caplog.at_level("INFO"):
        obs.log_resources("test")

    assert caplog.text == ""


def test_log_resources_emits_log(caplog):
    obs = Observability(
        config=ObservabilityConfig(resource_logging_enabled=True),
        process=FakeProcess(),
    )

    with caplog.at_level("INFO", logger="observability.resources"):
        obs.log_resources("worker-1")

    text = caplog.text

    assert "Resource usage" in text
    assert "worker-1" in text
    assert "150.0" in text  # memory MB
    assert "37.5" in text  # cpu %


def test_setup_registers_default_observability(monkeypatch):
    # Evitiamo psutil reale
    monkeypatch.setattr(
        "app.observability.psutil.Process",
        lambda pid: FakeProcess(),
    )

    obs = Observability.setup(enable_resource_logging=True)

    logger = get_logger("legacy.module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "legacy.module"


def test_legacy_log_resources_after_setup(monkeypatch, caplog):
    monkeypatch.setattr(
        "app.observability.psutil.Process",
        lambda pid: FakeProcess(),
    )

    Observability.setup(enable_resource_logging=True)

    with caplog.at_level("INFO", logger="observability.resources"):
        log_resources("legacy")

    assert "Resource usage" in caplog.text
    assert "legacy" in caplog.text


def test_legacy_log_resources_without_setup_is_noop(caplog):
    from app.observability import _reset_default_observability

    with caplog.at_level("INFO"):
        log_resources("no-setup")

    assert caplog.text == ""
