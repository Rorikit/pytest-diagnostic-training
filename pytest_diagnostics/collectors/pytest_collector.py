from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.core.models import DiagnosticFact, RuntimeException, RuntimeReport
from pytest_diagnostics.utils.time import now_epoch
from pytest_diagnostics.utils.traceback import format_exception


class PytestCollector(RuntimeCollector):
    name = "pytest"

    def start_test(self, context, item) -> None:
        context.add_fact(
            DiagnosticFact(
                name="pytest.nodeid",
                value=item.nodeid,
                source=self.name,
                timestamp=now_epoch(),
            )
        )
        markers = [marker.name for marker in item.iter_markers()]
        if markers:
            context.add_fact(
                DiagnosticFact(
                    name="pytest.markers",
                    value=markers,
                    source=self.name,
                    timestamp=now_epoch(),
                )
            )

    def after_report(self, context, report, call) -> None:
        context.reports.append(
            RuntimeReport(
                phase=report.when,
                outcome=report.outcome,
                duration=getattr(report, "duration", None),
                longrepr=str(report.longrepr) if getattr(report, "longrepr", None) else None,
            )
        )
        context.add_fact(
            DiagnosticFact(
                name=f"pytest.{report.when}.outcome",
                value=report.outcome,
                source=self.name,
                phase=report.when,
                timestamp=now_epoch(),
                metadata={"duration": getattr(report, "duration", None)},
            )
        )
        if call.excinfo is not None:
            exc = call.excinfo.value
            context.exceptions.append(
                RuntimeException(
                    exc_type=type(exc).__name__,
                    message=str(exc),
                    phase=report.when,
                    traceback=format_exception(call.excinfo.type, exc, call.excinfo.tb),
                )
            )
            context.add_fact(
                DiagnosticFact(
                    name="pytest.exception",
                    value=type(exc).__name__,
                    source=self.name,
                    phase=report.when,
                    timestamp=now_epoch(),
                    metadata={"message": str(exc)},
                )
            )

