from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, signal_text
from pytest_diagnostics.signals.models import DiagnosticSignal


class TimeoutRule(DiagnosticRule):
    name = "timeout"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = _combined_text(signals)
        if "timeout" not in text and "timed out" not in text:
            return None
        return DiagnosticFinding(
            area="Timeout/service availability",
            title="Timeout signal detected",
            explanation="Runtime signals contain timeout wording.",
            confidence=0.6,
            facts=["timeout signal detected"],
            assumptions=[
                "service responded too slowly",
                "network/environment issue",
            ],
            recommended_checks=[
                "inspect service latency",
                "check timeout configuration",
                "verify environment health",
            ],
            rule_name=self.name,
        )


class ConnectionRule(DiagnosticRule):
    name = "connection"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = _combined_text(signals)
        if "connection" not in text and "connect" not in text and "redis" not in text:
            return None
        return DiagnosticFinding(
            area="Infrastructure/network",
            title="Connection-related signal detected",
            explanation="Runtime signals contain connection-related wording.",
            confidence=0.6,
            facts=["connection-related signal detected"],
            assumptions=[
                "service unavailable",
                "network issue",
            ],
            recommended_checks=[
                "verify dependency health",
                "check DNS/proxy/TLS configuration",
                "retry direct request outside the test runner",
            ],
            rule_name=self.name,
        )


def _combined_text(signals: list[DiagnosticSignal]) -> str:
    return "\n".join(
        [
            signal_text(signals, "exception_message"),
            signal_text(signals, "allure_step"),
            signal_text(signals, "step_error"),
        ]
    )

