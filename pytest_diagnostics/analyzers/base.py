from __future__ import annotations

from abc import ABC, abstractmethod

from pytest_diagnostics.core.models import DiagnosticResult, TestDiagnosticContext


class DiagnosticAnalyzer(ABC):
    @abstractmethod
    def analyze(self, context: TestDiagnosticContext) -> DiagnosticResult:
        pass

