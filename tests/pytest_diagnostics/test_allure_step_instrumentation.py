import allure
import pytest

from pytest_diagnostics.core.context import set_current_context
from pytest_diagnostics.core.models import RuntimeException, RuntimeStep, TestDiagnosticContext
from pytest_diagnostics.engine.matcher import DiagnosticMatcher
from pytest_diagnostics.rules import default_rules
from pytest_diagnostics.signals.collectors import ContextSignalCollector
from pytest_diagnostics.steps.semantics import StepSemanticAnalyzer


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
    assert set(context.steps[0].tags) >= {"api", "ui", "comparison"}
    assert any(signal.type == "allure_step_failed" for signal in context.signals)


def test_allure_step_rule_prioritizes_api_ui_correlation():
    context = TestDiagnosticContext(nodeid="tests/test_steps.py::test_case", started_at=0)
    context.exceptions.append(
        RuntimeException(exc_type="AssertionError", message="assert api_members == ui_members", phase="call")
    )
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

    signals = ContextSignalCollector().collect(context)
    result = DiagnosticMatcher(default_rules()).match(signals)

    assert result.top_finding is not None
    assert result.top_finding.area == "Сравнение данных"
    assert result.top_finding.rule_name == "assertion_mismatch"


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

    signals = ContextSignalCollector().collect(context)
    result = DiagnosticMatcher(default_rules()).match(signals)

    assert result.top_finding is not None
    assert result.top_finding.area == "Timeout/доступность сервиса"


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

    signals = ContextSignalCollector().collect(context)
    result = DiagnosticMatcher(default_rules()).match(signals)

    assert result.top_finding is not None
    assert result.top_finding.area == "Инфраструктура/сеть"


def test_step_semantics_do_not_treat_redis_port_as_http_status():
    semantic = StepSemanticAnalyzer().analyze("Проверка Redis mock dependency: redis://localhost:6379 недоступен")

    assert "http_status" not in semantic.metadata
    assert "dependency" in semantic.tags
