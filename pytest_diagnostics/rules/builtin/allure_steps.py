from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticHypothesis, RuntimeStep, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class AllureStepCorrelationRule(DiagnosticRule):
    rule_id = "builtin.allure_step_correlation"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        failed_step = self._failed_step(context)
        if failed_step is None:
            return None

        tags = set(failed_step.tags)
        all_tags = {tag for step in context.steps for tag in step.tags}
        evidence = [f"упал allure.step: {failed_step.title}"]
        confidence = 0.55 + float(failed_step.metadata.get("confidence_hint", 0.0))

        if "compare" in tags and {"api", "ui"}.issubset(all_tags):
            confidence += 0.18
            evidence.append("до падения были шаги API и UI")
            return DiagnosticHypothesis(
                area="Синхронизация данных между API и UI",
                confidence=clamp_confidence(confidence),
                possible_causes=(
                    "UI показывает устаревшие данные",
                    "API и UI читают данные из разных источников или с разной задержкой",
                    "расхождение в порядке, фильтрации или нормализации данных",
                ),
                recommended_checks=(
                    "сравнить payload API и состояние UI в момент падения",
                    "проверить timestamps обновления данных",
                    "проверить cache invalidation и правила сортировки",
                ),
                evidence=tuple(evidence),
                rule_id=self.rule_id,
            )

        if "api" in tags:
            status = self._status(failed_step)
            if status is not None and status >= 500:
                confidence += 0.16
                area = "Ошибка backend/API"
                causes = (
                    "API вернул серверную ошибку",
                    "зависимость backend-сервиса находится в нерабочем состоянии",
                )
                checks = (
                    "проверить backend-логи по endpoint из шага",
                    "сопоставить падение с upstream-зависимостями",
                    "проверить payload и response body",
                )
            elif status in (401, 403):
                confidence += 0.18
                area = "Аутентификация или авторизация"
                causes = (
                    "сессия истекла или невалидна",
                    "у пользователя недостаточно прав",
                    "endpoint требует другую роль или scope",
                )
                checks = (
                    "проверить создание сессии/токена",
                    "сверить роль пользователя и permissions endpoint",
                    "проверить заголовки авторизации",
                )
            else:
                area = "API-интеграция"
                causes = (
                    "контракт API отличается от ожиданий теста",
                    "endpoint вернул неожиданные данные",
                )
                checks = (
                    "проверить endpoint, payload и response body",
                    "сверить контракт API с тестовыми ожиданиями",
                )
            if status is not None:
                evidence.append(f"в названии шага найден HTTP {status}")
            return DiagnosticHypothesis(
                area=area,
                confidence=clamp_confidence(confidence),
                possible_causes=causes,
                recommended_checks=checks,
                evidence=tuple(evidence),
                rule_id=self.rule_id,
            )

        if "timeout" in tags:
            confidence += 0.12
            return DiagnosticHypothesis(
                area="Timeout в шаге теста",
                confidence=clamp_confidence(confidence),
                possible_causes=(
                    "ожидаемое событие не наступило вовремя",
                    "сервис или UI отвечает медленнее таймаута теста",
                    "окружение перегружено или нестабильно",
                ),
                recommended_checks=(
                    "сравнить timeout шага с фактической длительностью",
                    "проверить retry/wait стратегию",
                    "проверить latency сервиса или UI",
                ),
                evidence=tuple(evidence),
                rule_id=self.rule_id,
            )

        if "dependency" in tags:
            confidence += 0.12
            return DiagnosticHypothesis(
                area="Внешняя зависимость или сетевой транспорт",
                confidence=clamp_confidence(confidence),
                possible_causes=(
                    "зависимость недоступна",
                    "соединение с внешним сервисом отклонено или разорвано",
                    "DNS, proxy, TLS или network-конфигурация некорректны",
                ),
                recommended_checks=(
                    "проверить health и адресуемость зависимости",
                    "проверить network/TLS/proxy настройки",
                    "повторить прямой запрос вне test runner",
                ),
                evidence=tuple(evidence),
                rule_id=self.rule_id,
            )

        if "ui" in tags:
            confidence += 0.1
            return DiagnosticHypothesis(
                area="Web UI / frontend",
                confidence=clamp_confidence(confidence),
                possible_causes=(
                    "страница или компонент не перешли в ожидаемое состояние",
                    "UI показывает устаревшие или неполные данные",
                    "селектор, ожидание или frontend-событие нестабильны",
                ),
                recommended_checks=(
                    "проверить состояние страницы в момент падения",
                    "сопоставить UI-события с network activity",
                    "проверить ожидания загрузки и cache",
                ),
                evidence=tuple(evidence),
                rule_id=self.rule_id,
            )

        return None

    def _failed_step(self, context: TestDiagnosticContext) -> RuntimeStep | None:
        for step in reversed(context.steps):
            if step.status == "failed":
                return step
        return None

    def _status(self, step: RuntimeStep) -> int | None:
        status = step.metadata.get("http_status")
        return status if isinstance(status, int) else None
