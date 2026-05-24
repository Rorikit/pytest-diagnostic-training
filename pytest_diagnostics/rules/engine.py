from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, DiagnosticResult, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule


class RuleEngine:
    def __init__(self, rules: list[DiagnosticRule] | None = None) -> None:
        self._rules = rules or []

    def register(self, rule: DiagnosticRule) -> None:
        self._rules.append(rule)

    def analyze(self, context: TestDiagnosticContext) -> DiagnosticResult:
        hypotheses: list[DiagnosticHypothesis] = []
        for rule in self._rules:
            hypothesis = rule.evaluate(context)
            if hypothesis is not None:
                hypotheses.append(hypothesis)
        hypotheses.sort(key=lambda item: item.confidence, reverse=True)
        status = "failed" if context.failed() else "passed"
        return DiagnosticResult(
            nodeid=context.nodeid,
            status=status,
            facts=tuple(context.facts),
            signals=tuple(context.signals),
            hypotheses=tuple(hypotheses),
        )

