from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.utils.time import now_epoch
from pytest_diagnostics.utils.traceback import compact_traceback


class TracebackCollector(RuntimeCollector):
    name = "traceback"

    def after_report(self, context, report, call) -> None:
        if call.excinfo is None:
            return
        compact = compact_traceback(
            context.exceptions[-1].traceback if context.exceptions else str(report.longrepr)
        )
        context.add_signal(
            DiagnosticSignal(
                type="traceback",
                value=compact or str(report.longrepr),
                source=self.name,
                severity="error",
                metadata={"exception_type": call.excinfo.typename, "phase": report.when},
            )
        )
