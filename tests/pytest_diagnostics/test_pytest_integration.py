from types import SimpleNamespace

from pytest_diagnostics.collectors.pytest_collector import PytestCollector
from pytest_diagnostics.collectors.timing_collector import TimingCollector
from pytest_diagnostics.core.lifecycle import DiagnosticLifecycle
from pytest_diagnostics.core.runtime import DiagnosticRuntime
from pytest_diagnostics.diagnostics.formatter import TextDiagnosticFormatter


class FakeWriter:
    def __init__(self) -> None:
        self.summary_model = None

    def write(self, summary_model):
        self.summary_model = summary_model
        return TextDiagnosticFormatter().format(summary_model)


class FakeExcInfo:
    type = AssertionError
    typename = "AssertionError"
    tb = None

    def __init__(self) -> None:
        self.value = AssertionError("assert 1 == 2")


def test_lifecycle_builds_signal_based_summary_from_pytest_report():
    writer = FakeWriter()
    runtime = DiagnosticRuntime(collectors=[PytestCollector(), TimingCollector()], writer=writer)
    lifecycle = DiagnosticLifecycle(runtime)
    item = SimpleNamespace(nodeid="tests/test_example.py::test_failure", iter_markers=lambda: [])
    report = SimpleNamespace(when="call", outcome="failed", failed=True, duration=0.01, longrepr="assert 1 == 2")
    call = SimpleNamespace(excinfo=FakeExcInfo())

    lifecycle.start_test(item)
    summary = lifecycle.after_report(item, report, call)
    lifecycle.finish_test(item)

    assert writer.summary_model is not None
    assert writer.summary_model.top_finding is not None
    assert writer.summary_model.top_finding.area == "Сравнение данных"
    assert "PYTEST DIAGNOSTICS" in summary
    assert "exception_type=AssertionError from pytest" in summary
