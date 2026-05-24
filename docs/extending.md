# Расширение

## Новое правило

Правило наследуется от `DiagnosticRule` и реализует `match`.

```python
from pytest_diagnostics.diagnostics.models import DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule
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

        return DiagnosticFinding(
            area="Cache",
            title="Cache-related signal detected",
            explanation="Runtime signals mention cache.",
            confidence=0.55,
            facts=["cache-related step detected"],
            assumptions=["stale data may be involved"],
            recommended_checks=["inspect cache invalidation and timestamps"],
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

Если нужен новый тип шага, расширьте `StepSemanticExtractor`, а правило пусть
матчит соответствующие `DiagnosticSignal`.

## Принципы

* Не добавлять test-specific rules.
* Не читать приватные pytest internals.
* Не смешивать facts и assumptions.
* Не превращать rules в большой classifier.
* Каждое правило должно объяснять evidence через facts и confidence.
