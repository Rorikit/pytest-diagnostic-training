from __future__ import annotations

from abc import ABC
from typing import Any

from pytest_diagnostics.core.models import TestDiagnosticContext


class RuntimeCollector(ABC):
    """Base collector interface.

    Collectors observe lifecycle events and append facts/signals to a context.
    They should not infer probable causes.
    """

    name = "collector"

    def configure(self, config: Any) -> None:
        pass

    def start_test(self, context: TestDiagnosticContext, item: Any) -> None:
        pass

    def before_phase(self, context: TestDiagnosticContext, phase: str) -> None:
        pass

    def after_report(self, context: TestDiagnosticContext, report: Any, call: Any) -> None:
        pass

    def finish_test(self, context: TestDiagnosticContext) -> None:
        pass

    def unconfigure(self) -> None:
        pass

