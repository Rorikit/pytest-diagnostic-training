"""Diagnostic intelligence layer for pytest and Allure.

The package observes pytest runtime events and common client libraries,
turns them into facts/signals, and attaches a diagnostic summary to Allure.
"""

from pytest_diagnostics.core.models import (
    DiagnosticFact,
    DiagnosticHypothesis,
    DiagnosticResult,
    DiagnosticSignal,
    TestDiagnosticContext,
)

__all__ = [
    "DiagnosticFact",
    "DiagnosticHypothesis",
    "DiagnosticResult",
    "DiagnosticSignal",
    "TestDiagnosticContext",
]

