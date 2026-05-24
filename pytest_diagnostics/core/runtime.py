from __future__ import annotations

from pytest_diagnostics.collectors.allure_collector import AllureCollector
from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.collectors.httpx_collector import HttpxCollector
from pytest_diagnostics.collectors.pytest_collector import PytestCollector
from pytest_diagnostics.collectors.requests_collector import RequestsCollector
from pytest_diagnostics.collectors.timing_collector import TimingCollector
from pytest_diagnostics.collectors.traceback_collector import TracebackCollector
from pytest_diagnostics.core.context import set_current_context
from pytest_diagnostics.core.models import TestDiagnosticContext
from pytest_diagnostics.core.signal_store import SignalStore
from pytest_diagnostics.output.allure_writer import AllureDiagnosticWriter
from pytest_diagnostics.rules.builtin import default_rules
from pytest_diagnostics.rules.engine import RuleEngine
from pytest_diagnostics.utils.time import now_epoch


class DiagnosticRuntime:
    """Coordinates passive collection, analysis, and output for pytest."""

    def __init__(
        self,
        collectors: list[RuntimeCollector] | None = None,
        rule_engine: RuleEngine | None = None,
        store: SignalStore | None = None,
        writer: AllureDiagnosticWriter | None = None,
    ) -> None:
        self.collectors = collectors or [
            PytestCollector(),
            TracebackCollector(),
            TimingCollector(),
            RequestsCollector(),
            HttpxCollector(),
            AllureCollector(),
        ]
        self.rule_engine = rule_engine or RuleEngine(default_rules())
        self.store = store or SignalStore()
        self.writer = writer or AllureDiagnosticWriter()

    def configure(self, config) -> None:
        for collector in self.collectors:
            collector.configure(config)

    def start_test(self, item) -> TestDiagnosticContext:
        context = TestDiagnosticContext(nodeid=item.nodeid, started_at=now_epoch())
        self.store.put(context)
        set_current_context(context)
        for collector in self.collectors:
            collector.start_test(context, item)
        return context

    def before_phase(self, item, phase: str) -> None:
        context = self._context_for(item)
        set_current_context(context)
        if context is None:
            return
        for collector in self.collectors:
            collector.before_phase(context, phase)

    def after_report(self, item, report, call) -> str | None:
        context = self._context_for(item)
        set_current_context(context)
        if context is None:
            return None
        for collector in self.collectors:
            collector.after_report(context, report, call)
        if report.failed:
            result = self.rule_engine.analyze(context)
            return self.writer.write(result)
        return None

    def finish_test(self, item) -> None:
        context = self._context_for(item)
        if context is not None:
            context.finished_at = now_epoch()
            for collector in self.collectors:
                collector.finish_test(context)
        set_current_context(None)
        if context is not None:
            self.store.remove(context.nodeid)

    def unconfigure(self) -> None:
        for collector in reversed(self.collectors):
            collector.unconfigure()
        self.store.clear()
        set_current_context(None)

    def _context_for(self, item) -> TestDiagnosticContext | None:
        return self.store.get(item.nodeid)

