from __future__ import annotations

import re
from typing import Any

from pytest_diagnostics.core.models import TestDiagnosticContext
from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.steps.semantics import StepSemanticAnalyzer


class PytestReportSignalCollector:
    """Collects minimal signals directly from pytest report/call objects."""

    def collect(self, report: Any, call: Any) -> list[DiagnosticSignal]:
        signals = [
            DiagnosticSignal(
                type="failure_phase",
                value=getattr(report, "when", "unknown"),
                source="pytest",
            )
        ]
        excinfo = getattr(call, "excinfo", None)
        if excinfo is None:
            return signals
        exc = excinfo.value
        message = str(exc)
        signals.extend(
            [
                DiagnosticSignal(type="exception_type", value=type(exc).__name__, source="pytest"),
                DiagnosticSignal(type="exception_message", value=message, source="pytest"),
            ]
        )
        signals.extend(_http_status_signals(message, source="pytest/message"))
        return signals


class ContextSignalCollector:
    """Converts collected runtime context into rule-engine signals."""

    def __init__(self, step_analyzer: StepSemanticAnalyzer | None = None) -> None:
        self._step_analyzer = step_analyzer or StepSemanticAnalyzer()

    def collect(self, context: TestDiagnosticContext) -> list[DiagnosticSignal]:
        signals: list[DiagnosticSignal] = []
        for report in context.reports:
            if report.outcome == "failed":
                signals.append(
                    DiagnosticSignal(
                        type="failure_phase",
                        value=report.phase,
                        source="pytest",
                        metadata={"duration": report.duration},
                    )
                )
        for exception in context.exceptions:
            signals.extend(
                [
                    DiagnosticSignal(
                        type="exception_type",
                        value=exception.exc_type,
                        source="pytest",
                        metadata={"phase": exception.phase},
                        severity="error",
                    ),
                    DiagnosticSignal(
                        type="exception_message",
                        value=exception.message,
                        source="pytest",
                        metadata={"phase": exception.phase},
                        severity="error",
                    ),
                ]
            )
            signals.extend(_http_status_signals(exception.message, source="pytest/message"))
        for step in context.steps:
            semantic = self._step_analyzer.analyze(step.title)
            signals.append(
                DiagnosticSignal(
                    type="allure_step",
                    value=step.title,
                    source="allure",
                    metadata={"status": step.status, "tags": step.tags, "duration_ms": step.duration_ms},
                    severity="error" if step.status == "failed" else None,
                )
            )
            if step.status == "failed":
                signals.append(
                    DiagnosticSignal(
                        type="failed_step",
                        value=step.title,
                        source="allure",
                        metadata={"tags": step.tags, "error": step.error},
                        severity="error",
                    )
                )
            if step.error:
                signals.append(
                    DiagnosticSignal(
                        type="step_error",
                        value=step.error,
                        source="allure",
                        metadata={"title": step.title, "tags": step.tags},
                        severity="error",
                    )
                )
            signals.extend(semantic.to_signals())
            http_status = step.metadata.get("http_status")
            if http_status is not None:
                signals.append(
                    DiagnosticSignal(
                        type="http_status",
                        value=http_status,
                        source="allure_step",
                        metadata={"title": step.title, "endpoint": step.metadata.get("endpoint")},
                    )
                )
            for tag in step.tags:
                signals.append(
                    DiagnosticSignal(
                        type="step_tag",
                        value=tag,
                        source="allure",
                        metadata={"title": step.title, "status": step.status},
                    )
                )
        for event in context.network_events:
            if event.status_code is not None:
                signals.append(
                    DiagnosticSignal(
                        type="http_status",
                        value=event.status_code,
                        source=event.library,
                        metadata={"method": event.method, "url": event.url, "elapsed_ms": event.elapsed_ms},
                    )
                )
            if event.error:
                signals.append(
                    DiagnosticSignal(
                        type="connection_error",
                        value=event.error,
                        source=event.library,
                        metadata={"method": event.method, "url": event.url},
                        severity="error",
                    )
                )
        return _deduplicate(signals)


def _http_status_signals(message: str, *, source: str) -> list[DiagnosticSignal]:
    return [
        DiagnosticSignal(type="http_status", value=int(match.group(1)), source=source)
        for match in re.finditer(r"\b([1-5]\d\d)\b", message)
    ]


def _deduplicate(signals: list[DiagnosticSignal]) -> list[DiagnosticSignal]:
    result: list[DiagnosticSignal] = []
    seen: set[tuple[str, str, str]] = set()
    for signal in signals:
        key = (signal.type, str(signal.value), signal.source)
        if key in seen:
            continue
        seen.add(key)
        result.append(signal)
    return result
