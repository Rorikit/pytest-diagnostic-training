from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class HttpStatusRule(DiagnosticRule):
    rule_id = "builtin.http_status"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        events = [event for event in context.network_events if event.status_code is not None and event.status_code >= 400]
        if not events:
            return None
        worst = max(events, key=lambda event: event.status_code or 0)
        status = worst.status_code or 0
        area = "HTTP-интеграция клиента и сервера"
        causes = ["удаленный endpoint вернул неуспешный HTTP-статус"]
        checks = ["проверить URL запроса, payload, тело ответа и серверные логи"]
        confidence = 0.55
        if status in (401, 403):
            area = "Аутентификация или авторизация"
            causes = ["сессия истекла или невалидна", "у пользователя недостаточно прав", "endpoint требует другую роль"]
            checks = ["проверить создание токена/сессии", "проверить эффективную роль пользователя", "сверить модель прав endpoint"]
            confidence = 0.8
        elif status >= 500:
            area = "Ошибка backend-сервиса"
            causes = ["сервис вернул внутреннюю ошибку", "зависимость за endpoint находится в нерабочем состоянии"]
            checks = ["проверить backend-логи", "проверить состояние upstream-зависимостей", "сопоставить с деплоем или инфраструктурными событиями"]
            confidence = 0.75
        elif status == 404:
            area = "Доступность endpoint или ресурса"
            causes = ["ресурс не существует", "route или base URL указаны неверно"]
            checks = ["проверить идентификаторы ресурса", "проверить настроенный base URL и route"]
            confidence = 0.7
        return DiagnosticHypothesis(
            area=area,
            confidence=clamp_confidence(confidence),
            possible_causes=tuple(causes),
            recommended_checks=tuple(checks),
            evidence=(f"{worst.library} {worst.method} {worst.url} вернул HTTP {status}",),
            rule_id=self.rule_id,
        )
