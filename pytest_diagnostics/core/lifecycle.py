from __future__ import annotations

from pytest_diagnostics.core.runtime import DiagnosticRuntime


class DiagnosticLifecycle:
    """Thin application service used by pytest hooks."""

    def __init__(self, runtime: DiagnosticRuntime | None = None) -> None:
        self.runtime = runtime or DiagnosticRuntime()

    def configure(self, config) -> None:
        self.runtime.configure(config)

    def start_test(self, item) -> None:
        self.runtime.start_test(item)

    def before_phase(self, item, phase: str) -> None:
        self.runtime.before_phase(item, phase)

    def after_report(self, item, report, call) -> str | None:
        return self.runtime.after_report(item, report, call)

    def finish_test(self, item) -> None:
        self.runtime.finish_test(item)

    def unconfigure(self) -> None:
        self.runtime.unconfigure()

