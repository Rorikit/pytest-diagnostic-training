from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, confidence_from, first_signal, has_signal
from pytest_diagnostics.signals.models import DiagnosticSignal


class ServerErrorRule(DiagnosticRule):
    name = "server_error"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        status_signal = first_signal(signals, "http_status")
        if status_signal is None:
            return None
        try:
            status = int(status_signal.value)
        except (TypeError, ValueError):
            return None
        if status < 500:
            return None
        evidence = [DiagnosticEvidence(f"Обнаружен HTTP статус {status}", 0.65, status_signal)]
        if has_signal(signals, "step_kind", "api_request"):
            evidence.append(DiagnosticEvidence("Обнаружен шаг API-запроса", 0.07, None))
        return DiagnosticFinding(
            area="API/backend",
            title="Обнаружен серверный HTTP статус",
            explanation=f"Runtime-сигналы содержат HTTP {status}.",
            confidence=confidence_from(evidence),
            facts=[f"обнаружен HTTP статус {status}"],
            assumptions=[
                "сервис вернул внутреннюю ошибку",
                "backend-зависимость может быть недоступна или нестабильна",
            ],
            recommended_checks=[
                "проверить backend-логи",
                "проверить upstream-зависимости",
                "проверить payload запроса и тело ответа",
            ],
            evidence=evidence,
            rule_name=self.name,
        )
