from __future__ import annotations

from contextvars import ContextVar

from pytest_diagnostics.core.models import TestDiagnosticContext

_current_context: ContextVar[TestDiagnosticContext | None] = ContextVar(
    "pytest_diagnostics_current_context",
    default=None,
)


def set_current_context(context: TestDiagnosticContext | None) -> None:
    _current_context.set(context)


def get_current_context() -> TestDiagnosticContext | None:
    return _current_context.get()

