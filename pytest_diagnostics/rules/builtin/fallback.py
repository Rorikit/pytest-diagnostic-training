from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule


class FallbackFailureRule(DiagnosticRule):
    rule_id = "builtin.fallback"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        if not context.failed():
            return None
        evidence = []
        if context.exceptions:
            evidence.append(f"{context.exceptions[-1].exc_type}: {context.exceptions[-1].message}")
        return DiagnosticHypothesis(
            area="Неизвестная область падения",
            confidence=0.25,
            possible_causes=("собрано недостаточно диагностических сигналов",),
            recommended_checks=(
                "проверить traceback и шаги Allure",
                "включить релевантные runtime-коллекторы",
                "добавить framework-level instrumentation для недостающей подсистемы",
            ),
            evidence=tuple(evidence),
            rule_id=self.rule_id,
        )
