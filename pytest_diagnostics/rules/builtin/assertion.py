from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class AssertionFailureRule(DiagnosticRule):
    rule_id = "builtin.assertion"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        assertions = [exc for exc in context.exceptions if exc.exc_type == "AssertionError"]
        if not assertions:
            return None
        evidence = ["зафиксирован AssertionError"]
        confidence = 0.45
        if context.network_events:
            ok_events = [event for event in context.network_events if event.status_code and event.status_code < 400]
            if ok_events:
                confidence += 0.15
                evidence.append("сетевые вызовы завершились без HTTP-ошибок")
        if any("==" in exc.message or "!=" in exc.message for exc in assertions):
            confidence += 0.1
            evidence.append("сообщение assertion содержит операторы сравнения")
        return DiagnosticHypothesis(
            area="Проверка данных или сравнение состояния",
            confidence=clamp_confidence(confidence),
            possible_causes=(
                "фактическое runtime-состояние отличается от ожидаемого",
                "расхождение в сортировке, порядке или нормализации данных",
                "задержка синхронизации между системами",
            ),
            recommended_checks=(
                "сравнить исходные actual/expected значения",
                "проверить правила сортировки и нормализации",
                "сопоставить предыдущие сетевые вызовы и временные метки",
            ),
            evidence=tuple(evidence),
            rule_id=self.rule_id,
        )
