from pytest_diagnostics.signals.models import DiagnosticSignal


def test_diagnostic_signal_describes_type_value_and_source():
    signal = DiagnosticSignal(
        type="exception_type",
        value="AssertionError",
        source="pytest",
        metadata={"phase": "call"},
        severity="error",
    )

    assert signal.describe() == "exception_type=AssertionError from pytest"
    assert signal.metadata["phase"] == "call"
    assert signal.severity == "error"

