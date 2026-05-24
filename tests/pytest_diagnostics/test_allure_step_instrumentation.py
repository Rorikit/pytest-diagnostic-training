import allure
import pytest

from pytest_diagnostics.core.context import set_current_context
from pytest_diagnostics.core.models import RuntimeStep, TestDiagnosticContext
from pytest_diagnostics.rules.builtin import default_rules
from pytest_diagnostics.rules.engine import RuleEngine


def test_allure_step_wrapper_records_failed_step_and_semantic_tags():
    context = TestDiagnosticContext(nodeid="tests/test_steps.py::test_case", started_at=0)
    set_current_context(context)

    try:
        with pytest.raises(AssertionError):
            with allure.step("Сравнение API Members и UI Members"):
                raise AssertionError("api != ui")
    finally:
        set_current_context(None)

    assert context.steps[0].title == "Сравнение API Members и UI Members"
    assert context.steps[0].status == "failed"
    assert set(context.steps[0].tags) >= {"api", "ui", "compare"}
    assert any(signal.kind == "allure.step_failed" for signal in context.signals)


def test_allure_step_rule_prioritizes_api_ui_correlation():
    context = TestDiagnosticContext(nodeid="tests/test_steps.py::test_case", started_at=0)
    context.steps.extend(
        [
            RuntimeStep(title="GET /redfish/v1/Chassis", status="passed", started_at=0, tags=("api",)),
            RuntimeStep(title="Получение Members из Web UI", status="passed", started_at=0, tags=("ui",)),
            RuntimeStep(
                title="Сравнение API Members и UI Members",
                status="failed",
                started_at=0,
                tags=("api", "ui", "compare"),
                metadata={"confidence_hint": 0.12},
            ),
        ]
    )

    result = RuleEngine(default_rules()).analyze(context)

    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.area == "Синхронизация данных между API и UI"
    assert result.primary_hypothesis.rule_id == "builtin.allure_step_correlation"


def test_allure_step_rule_uses_timeout_tag_before_ui_tag():
    context = TestDiagnosticContext(nodeid="tests/test_steps.py::test_timeout", started_at=0)
    context.steps.append(
        RuntimeStep(
            title="Ожидание Web UI страницы Dashboard timeout 30s",
            status="failed",
            started_at=0,
            tags=("ui", "timeout"),
            metadata={"confidence_hint": 0.08},
        )
    )

    result = RuleEngine(default_rules()).analyze(context)

    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.area == "Timeout в шаге теста"


def test_allure_step_rule_uses_dependency_tag():
    context = TestDiagnosticContext(nodeid="tests/test_steps.py::test_dependency", started_at=0)
    context.steps.append(
        RuntimeStep(
            title="Проверка dependency Redis connection",
            status="failed",
            started_at=0,
            tags=("dependency",),
            metadata={"confidence_hint": 0.04},
        )
    )

    result = RuleEngine(default_rules()).analyze(context)

    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.area == "Внешняя зависимость или сетевой транспорт"
