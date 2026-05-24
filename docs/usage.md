# Использование

## Подключение

В текущем проекте plugin уже подключен через `conftest.py`:

```python
pytest_plugins = ["pytest_diagnostics.plugin"]
```

Для отдельного пакета также доступен entry point `pytest11` из `pyproject.toml`.

## Два разных режима запуска

### Проверка библиотеки

Обычная команда:

```bash
py -m pytest
```

использует настройку из `pytest.ini`:

```ini
testpaths = tests
```

Поэтому запускаются только unit-тесты библиотеки. Нормальный результат:

```text
13 passed
```

### Демонстрация диагностики

Падающие сценарии лежат отдельно в `examples/`, чтобы штатный test suite
оставался зеленым.

Запуск:

```bash
py -m pytest examples/test_passive_diagnostics.py --diagnostics-append-longrepr -q
```

Нормальный результат для демонстрации:

```text
5 failed
```

Это не ошибка проекта. Эти тесты специально падают, чтобы показать
диагностические резюме.

## Allure output

При падении теста библиотека прикладывает:

* описание теста в `Overview`, чтобы резюме было видно сразу;
* `Диагностическое резюме` - человекочитаемый markdown-текст.
* `Runtime-снимок диагностики` - JSON для последующего анализа.

В некоторых версиях `allure-pytest` нет `allure.attachment_type.MARKDOWN`.
В этом случае summary прикладывается как `TEXT`, чтобы диагностический слой не
мог сломать pytest run.

## Что нужно делать в тестах

Ничего специального, кроме нормального использования `allure.step`.

Основной источник диагностики - названия `allure.step`.

Тесты не должны:

* создавать `DiagnosticFact` вручную;
* пушить runtime-события вручную;
* указывать вероятные причины;
* знать о rule engine.

Сигналы собираются пассивно из `allure.step`, pytest lifecycle, traceback,
timing, `requests` и `httpx`.

Хорошая практика для step-driven диагностики:

```python
with allure.step("API GET /redfish/v1/Chassis вернул HTTP 200"):
    ...

with allure.step("Получение Members из Web UI"):
    ...

with allure.step("Сравнение API Members и UI Members"):
    assert api_members == ui_members
```

Из таких шагов библиотека извлечет признаки `api`, `ui`, `compare`, HTTP status
и построит более точную гипотезу.

## Пример результата

```text
УПАЛ

Факты:
* стартовал allure.step: API POST /orders вернул HTTP 500
* allure.step 'API POST /orders вернул HTTP 500' завершился со статусом ошибка

Вероятная область проблемы:
Ошибка backend/API

Уверенность:
высокая

Возможные причины:
* API вернул серверную ошибку
* зависимость backend-сервиса находится в нерабочем состоянии

Рекомендуемые проверки:
* проверить backend-логи по endpoint из шага
* сопоставить падение с upstream-зависимостями
* проверить payload и response body
```

## Ограничения MVP

Текущая версия покрывает:

* `allure.step` instrumentation;
* pytest lifecycle;
* exceptions и traceback;
* timing;
* `requests`;
* `httpx`;
* markdown/JSON attachments в Allure.

Следующие естественные расширения:

* selenium collector;
* playwright collector;
* анализ flaky history;
* корреляция нескольких тестов;
* внешняя telemetry/export pipeline.
