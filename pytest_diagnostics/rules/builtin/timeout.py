from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class TimeoutRule(DiagnosticRule):
    rule_id = "builtin.timeout"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        texts = [exc.message.lower() for exc in context.exceptions]
        texts.extend(signal.message.lower() for signal in context.signals)
        if not any("timeout" in text or "timed out" in text for text in texts):
            return None
        confidence = 0.55
        evidence = ["в исключении или сигнале обнаружен признак timeout"]
        if any(event.error and "timeout" in event.error.lower() for event in context.network_events):
            confidence += 0.25
            evidence.append("сетевой клиент сообщил о timeout")
        if any(signal.kind == "timing.slow_phase" for signal in context.signals):
            confidence += 0.1
            evidence.append("pytest-фаза выполнялась дольше ожидаемого")
        return DiagnosticHypothesis(
            area="Timeout или медленный ответ сервиса",
            confidence=clamp_confidence(confidence),
            possible_causes=(
                "сервис отвечает слишком медленно",
                "timeout теста меньше фактической latency системы",
                "нестабильность окружения или сети",
            ),
            recommended_checks=(
                "проверить latency сервиса и retry-поведение",
                "сравнить timeout-настройки с фактической длительностью",
                "проверить состояние окружения на момент падения",
            ),
            evidence=tuple(evidence),
            rule_id=self.rule_id,
        )
