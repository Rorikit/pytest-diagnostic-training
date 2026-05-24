# Архитектура pytest-diagnostics

## Назначение

`pytest-diagnostics` — это диагностический intelligence layer для enterprise
automation frameworks. Он не заменяет Allure, не дублирует отчетность и не
требует ручного создания диагностических объектов в тестах.

Главная идея: тесты продолжают писать обычным способом через `allure.step(...)`,
а библиотека пассивно собирает runtime-сигналы из шагов и формирует гипотезы о
вероятной области проблемы.

## Поток данных

```text
pytest runtime
-> collectors
-> allure.step wrapper
-> TestDiagnosticContext
-> RuleEngine
-> DiagnosticResult
-> MarkdownSummaryBuilder
-> AllureDiagnosticWriter
```

## Слои

### pytest runtime

Файл `pytest_diagnostics/plugin.py` содержит только безопасные pytest hooks:

* `pytest_configure`
* `pytest_runtest_setup`
* `pytest_runtest_call`
* `pytest_runtest_makereport`
* `pytest_runtest_teardown`
* `pytest_unconfigure`

Hooks не содержат бизнес-логики. Они только пересылают lifecycle events в
`DiagnosticLifecycle`.

### Signal collection layer

Коллекторы находятся в `pytest_diagnostics/collectors`.

Их задача — наблюдать и записывать факты/сигналы:

* `PytestCollector` — outcome фаз, исключения, markers.
* `TracebackCollector` — traceback-сигналы.
* `TimingCollector` — длительность фаз и медленные фазы.
* `RequestsCollector` — HTTP-события `requests`.
* `HttpxCollector` — HTTP-события `httpx`.
* `AllureCollector` — включает instrumentation для `allure.step()`.

Коллекторы не делают выводов о причинах. Они только фиксируют наблюдения.

### Allure step instrumentation

`pytest_diagnostics/integrations/allure_steps.py` оборачивает публичный
`allure.step(title)`.

Обертка сохраняет:

* название шага;
* статус шага: `passed` или `failed`;
* длительность;
* exception внутри шага;
* semantic tags из названия шага: `api`, `ui`, `compare`, `auth`, `timeout`,
  `dependency`, `cache`;
* HTTP status и endpoint, если они указаны в названии шага.

Оригинальный Allure step продолжает выполняться. Библиотека только добавляет
диагностическое наблюдение вокруг него.

### Diagnostic model

Модели находятся в `pytest_diagnostics/core/models.py`.

Ключевое разделение:

* `DiagnosticFact` — наблюдаемый факт.
* `DiagnosticSignal` — нормализованный runtime-сигнал.
* `DiagnosticHypothesis` — предположение правила.
* `DiagnosticResult` — итог анализа.
* `TestDiagnosticContext` — per-test runtime context.
* `RuntimeStep` — runtime-представление `allure.step`.

Факты отделены от предположений, чтобы диагностика оставалась объяснимой.

### Rule engine

`RuleEngine` получает `TestDiagnosticContext` и запускает набор правил.

Правило:

* анализирует только доступные факты и сигналы;
* возвращает `DiagnosticHypothesis` только при наличии оснований;
* выставляет confidence score;
* добавляет possible causes, recommended checks и evidence.

Это позволяет расширять диагностику без большого `if/else` классификатора.

### Allure output

`AllureDiagnosticWriter` прикладывает к Allure:

* markdown summary;
* JSON runtime snapshot.

Allure остается основной системой отчета, а библиотека добавляет диагностический
контекст поверх существующего отчета.

## Runtime context

Каждый тест получает контекст по ключу `item.nodeid`.

Контекст хранит:

* facts;
* signals;
* exceptions;
* reports;
* timing;
* network events;
* attachments metadata.

Активный контекст доступен через `contextvars`, поэтому инструментирование
`requests` и `httpx` не требует ручного вызова из тестов.
