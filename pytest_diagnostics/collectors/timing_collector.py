from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.core.models import DiagnosticFact
from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.utils.time import now_epoch


class TimingCollector(RuntimeCollector):
    name = "timing"

    def after_report(self, context, report, call) -> None:
        duration = getattr(report, "duration", None)
        if duration is None:
            return
        context.add_fact(
            DiagnosticFact(
                name=f"timing.{report.when}.duration_ms",
                value=round(duration * 1000, 3),
                source=self.name,
                phase=report.when,
                timestamp=now_epoch(),
            )
        )
        if duration >= 5:
            context.add_signal(
                DiagnosticSignal(
                    type="slow_phase",
                    value=duration,
                    source=self.name,
                    severity="warning",
                    metadata={"phase": report.when, "duration_seconds": duration},
                )
            )
