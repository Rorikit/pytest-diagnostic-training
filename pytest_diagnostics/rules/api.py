from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, first_signal
from pytest_diagnostics.signals.models import DiagnosticSignal


class ServerErrorRule(DiagnosticRule):
    name = "server_error"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        status_signal = first_signal(signals, "http_status")
        if status_signal is None:
            return None
        try:
            status = int(status_signal.value)
        except (TypeError, ValueError):
            return None
        if status < 500:
            return None
        return DiagnosticFinding(
            area="API/backend",
            title="Server error status detected",
            explanation=f"Runtime signals contain HTTP {status}.",
            confidence=0.72,
            facts=[f"HTTP status {status} detected"],
            assumptions=[
                "service returned an internal error",
                "backend dependency may be unhealthy",
            ],
            recommended_checks=[
                "inspect backend logs",
                "check upstream dependencies",
                "verify request payload and response body",
            ],
            rule_name=self.name,
        )

