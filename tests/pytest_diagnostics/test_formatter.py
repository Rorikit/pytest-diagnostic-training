from pytest_diagnostics.diagnostics.formatter import TextDiagnosticFormatter
from pytest_diagnostics.diagnostics.models import DiagnosticFinding, DiagnosticSummary
from pytest_diagnostics.signals.models import DiagnosticSignal


def test_formatter_outputs_facts_assumptions_and_raw_signals():
    summary = DiagnosticSummary(
        findings=[
            DiagnosticFinding(
                area="Data comparison",
                title="Assertion mismatch",
                explanation="Test failed with AssertionError.",
                confidence=0.45,
                facts=["test failed with AssertionError"],
                assumptions=["actual and expected values are different"],
                recommended_checks=["inspect compared values"],
                rule_name="assertion_mismatch",
            )
        ],
        raw_signals=[DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest")],
    )

    text = TextDiagnosticFormatter().format(summary)

    assert "PYTEST DIAGNOSTICS" in text
    assert "Known facts:" in text
    assert "Most probable area:" in text
    assert "Data comparison" in text
    assert "exception_type=AssertionError from pytest" in text
