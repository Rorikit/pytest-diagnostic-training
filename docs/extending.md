# Расширение

## Новое правило

Правило наследуется от `DiagnosticRule` и реализует `match`.

```python
from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, confidence_from
from pytest_diagnostics.signals.models import DiagnosticSignal


class CacheSignalRule(DiagnosticRule):
    name = "cache_signal"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        has_cache_step = any(
            signal.type == "allure_step" and "cache" in str(signal.value).lower()
            for signal in signals
        )
        if not has_cache_step:
            return None

        evidence = [DiagnosticEvidence("Обнаружен cache-related шаг", 0.55)]
        return DiagnosticFinding(
            area="Cache",
            title="Обнаружен cache-related сигнал",
            explanation="Runtime-сигналы упоминают cache.",
            confidence=confidence_from(evidence),
            facts=["обнаружен cache-related шаг"],
            assumptions=["в проверке могли участвовать устаревшие данные"],
            recommended_checks=["проверить cache invalidation и timestamps"],
            evidence=evidence,
            rule_name=self.name,
        )
```

## Регистрация правила

Для framework-интеграции можно собрать свой runtime:

```python
from pytest_diagnostics.core.runtime import DiagnosticRuntime
from pytest_diagnostics.engine.matcher import DiagnosticMatcher
from pytest_diagnostics.rules import default_rules

runtime = DiagnosticRuntime(
    matcher=DiagnosticMatcher([*default_rules(), CacheSignalRule()]),
)
```

## Новый источник сигналов

Если нужно добавить новый runtime source, лучше делать это в два шага:

1. Collector пишет наблюдения в `TestDiagnosticContext`.
2. Signal collector переводит эти наблюдения в `DiagnosticSignal`.

Правила должны зависеть от сигналов, а не от конкретных pytest/allure объектов.

## Диагностика из allure.step

`pytest_diagnostics/integrations/allure_steps.py` оборачивает публичный
`allure.step()`. Из названия шага извлекаются semantic tags и HTTP status.

Если нужен новый тип шага, расширьте `StepSemanticAnalyzer` и/или patterns, а правило пусть
матчит соответствующие `DiagnosticSignal`.

В текущей архитектуре semantic analyzer находится в
`pytest_diagnostics/steps/semantics.py`.

## Принципы

* Не добавлять test-specific rules.
* Не читать приватные pytest internals.
* Не смешивать facts и assumptions.
* Не превращать rules в большой classifier.
* Каждое правило должно объяснять evidence через facts и confidence.
