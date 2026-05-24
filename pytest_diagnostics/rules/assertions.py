from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.rules.base import (
    DiagnosticRule,
    confidence_from,
    has_signal,
    matching_signal,
    signal_values,
)
from pytest_diagnostics.signals.models import DiagnosticSignal


class AssertionMismatchRule(DiagnosticRule):
    name = "assertion_mismatch"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        assertion = matching_signal(signals, "exception_type", "AssertionError")
        if assertion is None:
            return None
        evidence = [DiagnosticEvidence("Обнаружен AssertionError", 0.35, assertion)]
        facts = ["тест завершился с AssertionError"]

        comparison = matching_signal(signals, "step_kind", "comparison")
        if comparison is not None:
            evidence.append(DiagnosticEvidence("Упавший шаг является сравнением", 0.20, comparison))
            facts.append("упавший шаг является шагом сравнения")

        compared_sources = signal_values(signals, "compared_sources")
        if any(set(value) >= {"api", "ui"} for value in compared_sources if isinstance(value, tuple)):
            evidence.append(DiagnosticEvidence("Сравниваются источники API/UI", 0.15, None))
            facts.append("сравнение затрагивает API и UI")

        data_entity = _preferred_data_entity(signals)
        if data_entity is not None:
            evidence.append(DiagnosticEvidence(f"Обнаружена сущность данных: {data_entity.value}", 0.05, data_entity))
            facts.append(f"сущность данных: {data_entity.value}")

        return DiagnosticFinding(
            area="Сравнение данных",
            title="Несовпадение ожидаемого и фактического результата",
            explanation="Тест завершился с AssertionError.",
            confidence=confidence_from(evidence),
            facts=facts,
            assumptions=[
                "фактические и ожидаемые значения отличаются",
                "значения могут отличаться порядком элементов",
                "в проверке могли участвовать устаревшие данные",
            ],
            recommended_checks=[
                "проверить сравниваемые значения",
                "проверить порядок элементов",
                "проверить, обновлялись ли данные во время теста",
            ],
            evidence=evidence,
            rule_name=self.name,
        )


class MissingFieldRule(DiagnosticRule):
    name = "missing_field"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        key_error = matching_signal(signals, "exception_type", "KeyError")
        if key_error is None:
            return None
        evidence = [DiagnosticEvidence("Обнаружен KeyError", 0.55, key_error)]
        if has_signal(signals, "step_kind", "api_request"):
            evidence.append(DiagnosticEvidence("Падение произошло в контексте API-запроса", 0.15, None))
        return DiagnosticFinding(
            area="Данные/схема",
            title="Отсутствует ожидаемое поле",
            explanation="Тест завершился с KeyError.",
            confidence=confidence_from(evidence),
            facts=["тест завершился с KeyError"],
            assumptions=[
                "ожидаемое поле отсутствует",
                "структура ответа могла измениться",
            ],
            recommended_checks=[
                "проверить payload ответа",
                "проверить версию схемы или фикстуры",
                "проверить изменения контракта producer-сервиса",
            ],
            evidence=evidence,
            rule_name=self.name,
        )


def _preferred_data_entity(signals: list[DiagnosticSignal]) -> DiagnosticSignal | None:
    entities = [signal for signal in signals if signal.type == "data_entity"]
    for signal in reversed(entities):
        title = str(signal.metadata.get("title", "")).lower()
        if "сравн" in title or "compare" in title:
            return signal
    return entities[-1] if entities else None
