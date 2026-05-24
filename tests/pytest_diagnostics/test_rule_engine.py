from pytest_diagnostics.core.models import (
    DiagnosticFact,
    NetworkEvent,
    RuntimeException,
    RuntimeReport,
    TestDiagnosticContext,
)
from pytest_diagnostics.rules.builtin import default_rules
from pytest_diagnostics.rules.engine import RuleEngine


def test_http_status_rule_prioritizes_auth_failures():
    context = TestDiagnosticContext(nodeid="tests/test_api.py::test_auth", started_at=0)
    context.reports.append(RuntimeReport(phase="call", outcome="failed"))
    context.network_events.append(
        NetworkEvent(
            library="requests",
            method="GET",
            url="https://example.test/secure",
            status_code=403,
            elapsed_ms=12.0,
        )
    )

    result = RuleEngine(default_rules()).analyze(context)

    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.area == "Аутентификация или авторизация"
    assert result.primary_hypothesis.confidence == 0.8


def test_assertion_rule_separates_fact_from_hypothesis():
    context = TestDiagnosticContext(nodeid="tests/test_ui.py::test_members", started_at=0)
    context.reports.append(RuntimeReport(phase="call", outcome="failed"))
    context.exceptions.append(
        RuntimeException(
            exc_type="AssertionError",
            message="assert api_members == ui_members",
            phase="call",
        )
    )
    context.facts.append(DiagnosticFact(name="pytest.exception", value="AssertionError", source="pytest"))

    result = RuleEngine(default_rules()).analyze(context)

    assert result.facts[0].value == "AssertionError"
    assert result.primary_hypothesis is not None
    assert result.primary_hypothesis.area == "Проверка данных или сравнение состояния"
    assert result.primary_hypothesis.rule_id == "builtin.assertion"
