import sys
from types import SimpleNamespace

from pytest_diagnostics.diagnostics.models import DiagnosticSummary
from pytest_diagnostics.output.allure_writer import AllureDiagnosticWriter
from pytest_diagnostics.signals.models import DiagnosticSignal


def test_allure_writer_attaches_signal_summary(monkeypatch):
    attachments = []
    descriptions = []

    fake_allure = SimpleNamespace(
        attachment_type=SimpleNamespace(TEXT="text/plain", JSON="application/json"),
        dynamic=SimpleNamespace(description=lambda body: descriptions.append(body)),
        attach=lambda body, name, attachment_type: attachments.append(
            {"body": body, "name": name, "attachment_type": attachment_type}
        ),
    )
    monkeypatch.setitem(sys.modules, "allure", fake_allure)

    summary_model = DiagnosticSummary(
        findings=[],
        raw_signals=[DiagnosticSignal(type="exception_type", value="AssertionError", source="pytest")],
    )

    summary = AllureDiagnosticWriter(include_snapshot=True).write(summary_model)

    assert "PYTEST DIAGNOSTICS" in summary
    assert descriptions == [summary]
    assert attachments[0]["name"] == "Диагностическое резюме"
    assert attachments[0]["attachment_type"] == "text/plain"
    assert attachments[1]["name"] == "Runtime-снимок диагностики"
    assert attachments[1]["attachment_type"] == "application/json"
