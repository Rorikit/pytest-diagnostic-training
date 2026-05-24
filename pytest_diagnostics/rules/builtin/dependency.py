from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class DependencyFailureRule(DiagnosticRule):
    rule_id = "builtin.dependency"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        errors = [event for event in context.network_events if event.error]
        if not errors:
            return None
        evidence = [f"{event.library} {event.method} {event.url}: {event.error}" for event in errors[:3]]
        confidence = 0.65 + min(len(errors), 3) * 0.05
        return DiagnosticHypothesis(
            area="Внешняя зависимость или сетевой транспорт",
            confidence=clamp_confidence(confidence),
            possible_causes=(
                "зависимость недоступна",
                "некорректны DNS, proxy, TLS или параметры соединения",
                "тестовое окружение не может достучаться до целевого сервиса",
            ),
            recommended_checks=(
                "проверить health и адресуемость зависимости",
                "проверить proxy/TLS/network-конфигурацию",
                "повторить прямой запрос вне test runner",
            ),
            evidence=tuple(evidence),
            rule_id=self.rule_id,
        )
