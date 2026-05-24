from __future__ import annotations

from threading import RLock

from pytest_diagnostics.core.models import TestDiagnosticContext


class SignalStore:
    """Thread-safe registry of per-test diagnostic contexts."""

    def __init__(self) -> None:
        self._contexts: dict[str, TestDiagnosticContext] = {}
        self._lock = RLock()

    def put(self, context: TestDiagnosticContext) -> None:
        with self._lock:
            self._contexts[context.nodeid] = context

    def get(self, nodeid: str) -> TestDiagnosticContext | None:
        with self._lock:
            return self._contexts.get(nodeid)

    def remove(self, nodeid: str) -> TestDiagnosticContext | None:
        with self._lock:
            return self._contexts.pop(nodeid, None)

    def clear(self) -> None:
        with self._lock:
            self._contexts.clear()

