import sys
from types import SimpleNamespace

from pytest_diagnostics.core.models import DiagnosticResult
from pytest_diagnostics.output.allure_writer import AllureDiagnosticWriter


def test_allure_writer_falls_back_when_markdown_type_is_missing(monkeypatch):
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

    result = DiagnosticResult(
        nodeid="tests/test_example.py::test_failure",
        status="failed",
        facts=(),
        signals=(),
        hypotheses=(),
    )

    summary = AllureDiagnosticWriter(include_snapshot=True).write(result)

    assert "УПАЛ" in summary
    assert descriptions == [summary]
    assert attachments[0]["name"] == "Диагностическое резюме"
    assert attachments[0]["attachment_type"] == "text/plain"
    assert attachments[1]["name"] == "Runtime-снимок диагностики"
    assert attachments[1]["attachment_type"] == "application/json"
