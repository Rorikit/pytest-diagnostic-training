from __future__ import annotations

import pytest

from pytest_diagnostics.core.lifecycle import DiagnosticLifecycle

_LIFECYCLE_KEY = "_pytest_diagnostics_lifecycle"


def pytest_addoption(parser) -> None:
    group = parser.getgroup("pytest-diagnostics")
    group.addoption(
        "--diagnostics-disable",
        action="store_true",
        default=False,
        help="Отключить сбор диагностического резюме.",
    )
    group.addoption(
        "--diagnostics-append-longrepr",
        action="store_true",
        default=False,
        help="Добавить диагностическое резюме в консольный вывод pytest при падении.",
    )


def pytest_configure(config) -> None:
    if config.getoption("--diagnostics-disable"):
        return
    lifecycle = DiagnosticLifecycle()
    lifecycle.configure(config)
    setattr(config, _LIFECYCLE_KEY, lifecycle)


def pytest_runtest_setup(item) -> None:
    lifecycle = _get_lifecycle(item.config)
    if lifecycle is None:
        return
    lifecycle.start_test(item)
    lifecycle.before_phase(item, "setup")


def pytest_runtest_call(item) -> None:
    lifecycle = _get_lifecycle(item.config)
    if lifecycle is not None:
        lifecycle.before_phase(item, "call")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    lifecycle = _get_lifecycle(item.config)
    if lifecycle is None:
        return
    summary = lifecycle.after_report(item, report, call)
    if summary and item.config.getoption("--diagnostics-append-longrepr"):
        report.longrepr = f"{report.longrepr}\n\n{summary}"
    if report.when == "teardown":
        lifecycle.finish_test(item)


def pytest_runtest_teardown(item) -> None:
    lifecycle = _get_lifecycle(item.config)
    if lifecycle is not None:
        lifecycle.before_phase(item, "teardown")


def pytest_unconfigure(config) -> None:
    lifecycle = _get_lifecycle(config)
    if lifecycle is not None:
        lifecycle.unconfigure()
        setattr(config, _LIFECYCLE_KEY, None)


def _get_lifecycle(config) -> DiagnosticLifecycle | None:
    return getattr(config, _LIFECYCLE_KEY, None)
