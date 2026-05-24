from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticFinding
from pytest_diagnostics.rules.base import DiagnosticRule, signal_text
from pytest_diagnostics.signals.models import DiagnosticSignal


class UnauthorizedRule(DiagnosticRule):
    name = "unauthorized"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = signal_text(signals, "exception_message") + "\n" + signal_text(signals, "allure_step")
        if "401" not in text and "unauthorized" not in text:
            return None
        return DiagnosticFinding(
            area="Auth",
            title="Unauthorized signal detected",
            explanation="Runtime signals contain 401 or Unauthorized.",
            confidence=0.75,
            facts=["unauthorized signal detected"],
            assumptions=["session is missing", "token is invalid"],
            recommended_checks=[
                "verify session creation",
                "check token validity",
                "inspect auth headers",
            ],
            rule_name=self.name,
        )


class ForbiddenRule(DiagnosticRule):
    name = "forbidden"

    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        text = signal_text(signals, "exception_message") + "\n" + signal_text(signals, "allure_step")
        if "403" not in text and "forbidden" not in text and "insufficient permissions" not in text:
            return None
        return DiagnosticFinding(
            area="Permissions",
            title="Forbidden or permissions signal detected",
            explanation="Runtime signals contain 403, Forbidden, or insufficient permissions.",
            confidence=0.75,
            facts=["forbidden/permissions signal detected"],
            assumptions=[
                "user does not have required role",
                "endpoint requires elevated permissions",
            ],
            recommended_checks=[
                "check effective user role",
                "verify endpoint permission model",
                "inspect auth scopes or privileges",
            ],
            rule_name=self.name,
        )

