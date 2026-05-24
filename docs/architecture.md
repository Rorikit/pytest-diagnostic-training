# Архитектура pytest-diagnostics

## Назначение

`pytest-diagnostics` - диагностический слой поверх `pytest` и Allure.

Библиотека не заменяет Allure и не создает новую систему отчетности. Она
собирает runtime-сигналы, прогоняет их через независимые правила и добавляет
диагностическое резюме в pytest/Allure output.

## Pipeline

```text
pytest / allure / runtime events
-> TestDiagnosticContext
-> DiagnosticSignal[]
-> DiagnosticMatcher
-> DiagnosticFinding[]
-> DiagnosticSummary
-> formatter / Allure writer
```

## Слои

### pytest plugin

`pytest_diagnostics/plugin.py` содержит только безопасные pytest hooks.

Hooks не классифицируют ошибки. Они пересылают lifecycle events в
`DiagnosticLifecycle`. При необходимости консольного вывода plugin добавляет
summary через `report.sections.append(("pytest-diagnostics", text))`.

### Runtime collection

`pytest_diagnostics/collectors` собирает runtime-наблюдения в
`TestDiagnosticContext`:

* pytest phase outcome;
* exceptions;
* traceback;
* timing;
* Allure steps;
* optional network events.

Коллекторы не делают выводов о причинах.

### Signal layer

`pytest_diagnostics/signals` переводит runtime context в плоский список
`DiagnosticSignal`.

Примеры:

```python
DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest")
DiagnosticSignal(type="failure_phase", value="call", source="pytest")
DiagnosticSignal(type="http_status", value=500, source="allure_step")
DiagnosticSignal(type="allure_step", value="API POST /orders вернул HTTP 500", source="allure")
```

`pytest_diagnostics/steps` добавляет semantic intelligence для названий
`allure.step`: `step_kind`, `endpoint`, `http_method`, `resource`, `domain`,
`role`, `data_entity`, `compared_sources`.

### Rule layer

`pytest_diagnostics/rules` содержит независимые правила. Правило получает только
`list[DiagnosticSignal]` и возвращает `DiagnosticFinding | None`.

Начальные правила:

* `AssertionMismatchRule`
* `MissingFieldRule`
* `UnauthorizedRule`
* `ForbiddenRule`
* `ServerErrorRule`
* `TimeoutRule`
* `ConnectionRule`

### Matching engine

`pytest_diagnostics/engine/matcher.py` запускает все rules, собирает findings и
сортирует их по `confidence desc`.

### Diagnostics model

`pytest_diagnostics/diagnostics` содержит:

* `DiagnosticFinding`
* `DiagnosticEvidence`
* `DiagnosticSummary`
* `TextDiagnosticFormatter`

`DiagnosticFinding` явно разделяет:

* `facts` - что реально известно из сигналов;
* `assumptions` - вероятные причины.

`DiagnosticEvidence` объясняет, из каких сигналов сложилась уверенность
finding. Confidence считается как сумма весов evidence с ограничением `0..1`.

## Последовательность шагов

`StepSequenceBuilder` строит упорядоченную последовательность шагов:

```text
1. auth: Логин под admin-сессией - passed
2. api_request: GET /redfish/v1/Chassis - passed
3. ui: Получение Members из Web UI - passed
4. comparison: Сравнение API Members и UI Members - failed
```

Это не полноценный dependency graph, но основа для будущего causal analysis.

### Allure output

`AllureDiagnosticWriter` пишет:

* description в Allure Overview;
* attachment `Диагностическое резюме`;
* attachment `Runtime-снимок диагностики`.

Allure остается основной системой отчета.
