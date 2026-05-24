# pytest-diagnostics

`pytest-diagnostics` - диагностический слой поверх `pytest` и Allure.

Библиотека не заменяет Allure и не пытается быть отдельной системой отчетности.
Она оборачивает публичный `allure.step()`, пассивно собирает runtime-факты и
сигналы из шагов, прогоняет их через набор расширяемых правил и прикладывает к
Allure понятное диагностическое резюме на русском языке.

## Важное про запуск

Команда:

```bash
py -m pytest
```

запускает штатные unit-тесты библиотеки из директории `tests/`. Поэтому
ожидаемый результат здесь:

```text
13 passed
```

Это проверка самой библиотеки, а не демонстрация падений.

Чтобы увидеть 5 специально падающих сценариев и диагностические резюме, нужно
запустить примеры отдельно:

```bash
py -m pytest examples/test_passive_diagnostics.py --diagnostics-append-longrepr -q
```

Ожидаемый результат:

```text
5 failed
```

Эти падения намеренные. Они показывают работу диагностики на основе
`allure.step(...)`.

## Что решает

Обычный результат:

```text
AssertionError
```

Результат с диагностическим слоем:

```text
УПАЛ

Факты:
* стартовал allure.step: API GET /redfish/v1/Chassis вернул HTTP 200
* allure.step 'Сравнение API Members и UI Members' завершился со статусом ошибка

Вероятная область проблемы:
Синхронизация данных между API и UI

Уверенность:
высокая

Возможные причины:
* UI показывает устаревшие данные
* API и UI читают данные из разных источников или с разной задержкой
* расхождение в порядке, фильтрации или нормализации данных

Рекомендуемые проверки:
* сравнить payload API и состояние UI в момент падения
* проверить timestamps обновления данных
* проверить cache invalidation и правила сортировки
```

## Архитектура

```text
pytest runtime
-> allure.step wrapper
-> слой сбора сигналов
-> диагностическая модель
-> rule engine
-> Allure summary output
```

Основные слои:

* `pytest_diagnostics.plugin` - тонкая интеграция с безопасными pytest hooks.
* `pytest_diagnostics.core` - runtime context, lifecycle, signal store, модели.
* `pytest_diagnostics.collectors` - пассивные сборщики runtime-сигналов.
* `pytest_diagnostics.integrations.allure_steps` - безопасная обертка `allure.step()`.
* `pytest_diagnostics.rules` - pluggable rule engine и встроенные правила.
* `pytest_diagnostics.output` - markdown-резюме и Allure attachments.

## Использование

Проектный `conftest.py` уже подключает plugin:

```python
pytest_plugins = ["pytest_diagnostics.plugin"]
```

Проверка библиотеки:

```bash
py -m pytest
```

Демонстрация падающих сценариев:

```bash
py -m pytest examples/test_passive_diagnostics.py --diagnostics-append-longrepr -q
```

Отключение диагностики:

```bash
py -m pytest --diagnostics-disable
```

По умолчанию диагностика прикладывается в Allure как:

* описание теста в `Overview`, чтобы резюме было видно без открытия attachment.
* `Диагностическое резюме` - markdown-текст.
* `Runtime-снимок диагностики` - JSON со структурированными фактами и сигналами.

Если установленная версия `allure-pytest` не содержит attachment type
`MARKDOWN`, summary безопасно прикладывается как обычный text attachment.

`--diagnostics-append-longrepr` дополнительно добавляет summary в консольный
pytest output. Это удобно для локальной отладки.

## Документация

* [Архитектура](docs/architecture.md)
* [Использование](docs/usage.md)
* [Расширение правилами и коллекторами](docs/extending.md)
