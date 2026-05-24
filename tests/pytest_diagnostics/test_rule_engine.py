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
    assert summary.top_finding.area == "Permissions"
    assert summary.top_finding.confidence == 0.75
    assert summary.findings[-1].area == "Data comparison"


def test_assertion_rule_separates_facts_from_assumptions():
    signals = [DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest")]

    summary = DiagnosticMatcher(default_rules()).match(signals)

    assert summary.top_finding is not None
    assert "test failed with AssertionError" in summary.top_finding.facts
    assert "actual and expected values are different" in summary.top_finding.assumptions

