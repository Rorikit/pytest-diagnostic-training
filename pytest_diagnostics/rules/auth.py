from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, confidence_from, matching_signal, signal_text
from pytest_diagnostics.signals.models import DiagnosticSignal


class UnauthorizedRule(DiagnosticRule):
    name = "unauthorized"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        status = matching_signal(signals, "http_status", 401)
        text = signal_text(signals, "exception_message") + "\n" + signal_text(signals, "allure_step")
        text_match = "401" in text or "unauthorized" in text
        if status is None and not text_match:
            return None
        evidence = []
        if status is not None:
            evidence.append(DiagnosticEvidence("Обнаружен HTTP статус 401", 0.65, status))
        if text_match:
            evidence.append(DiagnosticEvidence("Обнаружен текстовый сигнал Unauthorized", 0.40, None))
        return DiagnosticFinding(
            area="Аутентификация",
            title="Обнаружен сигнал Unauthorized",
            explanation="Runtime-сигналы содержат 401 или Unauthorized.",
            confidence=confidence_from(evidence),
            facts=["обнаружен сигнал unauthorized"],
            assumptions=["сессия отсутствует", "токен невалиден"],
            recommended_checks=[
                "проверить создание сессии",
                "проверить валидность токена",
                "проверить auth headers",
            ],
            evidence=evidence,
            rule_name=self.name,
        )


class ForbiddenRule(DiagnosticRule):
    name = "forbidden"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        status = matching_signal(signals, "http_status", 403)
        text = signal_text(signals, "exception_message") + "\n" + signal_text(signals, "allure_step")
        text_match = "403" in text or "forbidden" in text or "insufficient permissions" in text
        if status is None and not text_match:
            return None
        evidence = []
        if status is not None:
            evidence.append(DiagnosticEvidence("Обнаружен HTTP статус 403", 0.65, status))
        if text_match:
            evidence.append(DiagnosticEvidence("Обнаружен текстовый сигнал Forbidden/permissions", 0.40, None))
        return DiagnosticFinding(
            area="Права доступа",
            title="Обнаружен сигнал Forbidden или недостаточных прав",
            explanation="Runtime-сигналы содержат 403, Forbidden или insufficient permissions.",
            confidence=confidence_from(evidence),
            facts=["обнаружен сигнал forbidden/permissions"],
            assumptions=[
                "у пользователя нет требуемой роли",
                "endpoint требует повышенных прав",
            ],
            recommended_checks=[
                "проверить фактическую роль пользователя",
                "проверить модель прав endpoint",
                "проверить auth scopes или privileges",
            ],
            evidence=evidence,
            rule_name=self.name,
        )
