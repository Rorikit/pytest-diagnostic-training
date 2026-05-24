# Расширение

## Новое диагностическое правило

Правило наследуется от `DiagnosticRule` и реализует `evaluate`.

```python
from pytest_diagnostics.core.models import DiagnosticHypothesis, TestDiagnosticContext
from pytest_diagnostics.rules.base import DiagnosticRule, clamp_confidence


class CacheInvalidationRule(DiagnosticRule):
    rule_id = "custom.cache_invalidation"

    def evaluate(self, context: TestDiagnosticContext) -> DiagnosticHypothesis | None:
        has_successful_api = any(
            event.status_code and event.status_code < 400
            for event in context.network_events
        )
        has_assertion = any(
            exc.exc_type == "AssertionError"
            for exc in context.exceptions
        )

        if not has_successful_api or not has_assertion:
            return None

        return DiagnosticHypothesis(
            area="Синхронизация данных / UI cache",
            confidence=clamp_confidence(0.62),
            possible_causes=(
                "UI показывает устаревшие данные",
                "cache invalidation сработал позже проверки",
            ),
            recommended_checks=(
                "сравнить timestamps API и UI",
                "проверить cache headers и invalidate-события",
            ),
            evidence=("API ответил успешно, но проверка данных упала",),
            rule_id=self.rule_id,
        )
```

## Новый коллектор

Коллектор наследуется от `RuntimeCollector`.

```python
from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.core.models import DiagnosticFact
from pytest_diagnostics.utils.time import now_epoch


class BrowserCollector(RuntimeCollector):
    name = "browser"

    def after_report(self, context, report, call) -> None:
        if report.failed:
            context.add_fact(
                DiagnosticFact(
                    name="browser.page_url",
                    value="https://example.test/current",
                    source=self.name,
                    phase=report.when,
                    timestamp=now_epoch(),
                )
            )
```

Коллектор должен собирать наблюдения, но не делать выводов. Выводы остаются в
правилах.

## Диагностика из allure.step

Step-driven диагностика расширяется через semantic tags и правила.

Если нужно добавить новый тип шага, расширьте `StepSemanticExtractor` в
`pytest_diagnostics/integrations/allure_steps.py` новой regex-записью, а затем
добавьте правило, которое анализирует `context.steps`.

Пример: если в проекте есть шаги `MQ publish`, можно добавить tag `mq`, а
правило будет генерировать гипотезу про broker/queue subsystem.

## Композиция runtime

Для enterprise framework можно собрать собственный `DiagnosticRuntime`:

```python
from pytest_diagnostics.core.runtime import DiagnosticRuntime
from pytest_diagnostics.rules.engine import RuleEngine
from pytest_diagnostics.rules.builtin import default_rules

runtime = DiagnosticRuntime(
    collectors=[
        # стандартные и кастомные collectors
    ],
    rule_engine=RuleEngine([
        *default_rules(),
        CacheInvalidationRule(),
    ]),
)
```

## Принципы расширения

* Не добавлять test-specific rules.
* Не читать приватные pytest internals.
* Не смешивать факты и гипотезы.
* Не превращать правила в большой классификатор.
* Каждое правило должно объяснять evidence и confidence.
