from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, confidence_from, matching_signal, signal_text
from pytest_diagnostics.signals.models import DiagnosticSignal


class TimeoutRule(DiagnosticRule):
    name = "timeout"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = _combined_text(signals)
        timeout_step = matching_signal(signals, "step_kind", "timeout")
        text_match = "timeout" in text or "timed out" in text
        if timeout_step is None and not text_match:
            return None
        evidence = []
        if timeout_step is not None:
            evidence.append(DiagnosticEvidence("Обнаружен шаг типа timeout", 0.45, timeout_step))
        if text_match:
            evidence.append(DiagnosticEvidence("Обнаружен текстовый timeout-сигнал", 0.60, None))
        return DiagnosticFinding(
            area="Timeout/доступность сервиса",
            title="Обнаружен timeout-сигнал",
            explanation="Runtime-сигналы содержат timeout wording.",
            confidence=confidence_from(evidence),
            facts=["обнаружен timeout-сигнал"],
            assumptions=[
                "сервис отвечает слишком медленно",
                "возможна проблема сети или окружения",
            ],
            recommended_checks=[
                "проверить latency сервиса",
                "проверить timeout-конфигурацию",
                "проверить состояние окружения",
            ],
            evidence=evidence,
            rule_name=self.name,
        )


class ConnectionRule(DiagnosticRule):
    name = "connection"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = _combined_text(signals)
        dependency = matching_signal(signals, "step_kind", "dependency")
        text_match = "connection" in text or "connect" in text or "redis" in text
        if dependency is None and not text_match:
            return None
        evidence = []
        if dependency is not None:
            evidence.append(DiagnosticEvidence("Обнаружен шаг проверки зависимости", 0.35, dependency))
        if text_match:
            evidence.append(DiagnosticEvidence("Обнаружен текстовый connection-сигнал", 0.60, None))
        return DiagnosticFinding(
            area="Инфраструктура/сеть",
            title="Обнаружен connection-сигнал",
            explanation="Runtime-сигналы содержат connection-related wording.",
            confidence=confidence_from(evidence),
            facts=["обнаружен connection-сигнал"],
            assumptions=[
                "зависимый сервис недоступен",
                "возможна сетевая проблема",
            ],
            recommended_checks=[
                "проверить health и доступность зависимости",
                "проверить DNS/proxy/TLS конфигурацию",
                "повторить прямой запрос вне test runner",
            ],
            evidence=evidence,
            rule_name=self.name,
        )


def _combined_text(signals: list[DiagnosticSignal]) -> str:
    return "\n".join(
        [
            signal_text(signals, "exception_message"),
            signal_text(signals, "allure_step"),
            signal_text(signals, "step_error"),
        ]
    )
