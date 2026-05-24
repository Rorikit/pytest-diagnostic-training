from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticSummary


class TextDiagnosticFormatter:
    def format(self, summary: DiagnosticSummary) -> str:
        finding = summary.top_finding
        lines = ["==================== PYTEST DIAGNOSTICS ====================", "", "Known facts:"]
        if finding and finding.facts:
            lines.extend(f"- {fact}" for fact in finding.facts)
        else:
            lines.append("- no high-level facts matched by rules")

        lines.extend(["", "Most probable area:"])
        lines.append(finding.area if finding else "Unknown")

        lines.extend(["", "Confidence:"])
        lines.append(f"{finding.confidence:.2f}" if finding else "0.00")

        lines.extend(["", "Possible causes:"])
        if finding and finding.assumptions:
            lines.extend(f"- {assumption}" for assumption in finding.assumptions)
        else:
            lines.append("- not enough signals to infer probable causes")

        lines.extend(["", "Recommended checks:"])
        if finding and finding.recommended_checks:
            lines.extend(f"- {check}" for check in finding.recommended_checks)
        else:
            lines.append("- inspect traceback and Allure steps")

        lines.extend(["", "Raw signals:"])
        if summary.raw_signals:
            lines.extend(f"- {signal.describe()}" for signal in summary.raw_signals)
        else:
            lines.append("- no raw signals collected")

        lines.extend(["", "============================================================"])
        return "\n".join(lines)

