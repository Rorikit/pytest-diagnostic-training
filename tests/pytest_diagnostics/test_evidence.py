from pytest_diagnostics.diagnostics.models import DiagnosticEvidence
from pytest_diagnostics.rules.base import confidence_from


def test_confidence_from_evidence_grows_with_weights():
    evidence = [
        DiagnosticEvidence("first", 0.2),
        DiagnosticEvidence("second", 0.3),
    ]

    assert confidence_from(evidence) == 0.5


def test_confidence_from_evidence_clamps_to_one():
    evidence = [
        DiagnosticEvidence("first", 0.7),
        DiagnosticEvidence("second", 0.6),
    ]

    assert confidence_from(evidence) == 1.0

