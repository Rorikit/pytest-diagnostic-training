from pytest_diagnostics.engine.matcher import DiagnosticMatcher
from pytest_diagnostics.rules import default_rules
from pytest_diagnostics.signals.models import DiagnosticSignal


def test_matcher_sorts_findings_by_confidence():
    signals = [
        DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest"),
        DiagnosticSignal(type="exception_message", value="request returned 403 Forbidden", source="pytest"),
    ]

    summary = DiagnosticMatcher(default_rules()).match(signals)

    assert summary.top_finding is not None
    assert summary.top_finding.area == "Права доступа"
    assert summary.top_finding.confidence == 0.4
    assert summary.findings[-1].area == "Сравнение данных"


def test_assertion_rule_separates_facts_from_assumptions():
    signals = [DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest")]

    summary = DiagnosticMatcher(default_rules()).match(signals)

    assert summary.top_finding is not None
    assert "тест завершился с AssertionError" in summary.top_finding.facts
    assert "фактические и ожидаемые значения отличаются" in summary.top_finding.assumptions
    assert summary.top_finding.confidence == 0.35


def test_assertion_confidence_grows_with_comparison_context():
    signals = [
        DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest"),
        DiagnosticSignal(type="step_kind", value="comparison", source="step_semantics"),
    ]

    summary = DiagnosticMatcher(default_rules()).match(signals)

    assert summary.top_finding is not None
    assert summary.top_finding.confidence == 0.55


def test_assertion_confidence_grows_with_api_ui_sources():
    signals = [
        DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest"),
        DiagnosticSignal(type="step_kind", value="comparison", source="step_semantics"),
        DiagnosticSignal(type="compared_sources", value=("api", "ui"), source="step_semantics"),
        DiagnosticSignal(type="data_entity", value="members", source="step_semantics"),
    ]

    summary = DiagnosticMatcher(default_rules()).match(signals)

    assert summary.top_finding is not None
    assert summary.top_finding.confidence == 0.75
