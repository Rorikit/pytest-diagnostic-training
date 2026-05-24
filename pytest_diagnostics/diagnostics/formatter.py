from __future__ import annotations

from pytest_diagnostics.diagnostics.models import DiagnosticSummary


class TextDiagnosticFormatter:
    def __init__(self, max_raw_signals: int = 12) -> None:
        self._max_raw_signals = max_raw_signals

    def format(self, summary: DiagnosticSummary) -> str:
        finding = summary.top_finding
        lines = ["==================== PYTEST DIAGNOSTICS ====================", "", "Известные факты:"]
        if finding and finding.facts:
            lines.extend(f"- {fact}" for fact in finding.facts)
        else:
            lines.append("- правила не нашли высокоуровневых фактов")

        lines.extend(["", "Наиболее вероятная область:"])
        lines.append(finding.area if finding else "Не определена")

        lines.extend(["", "Уверенность:"])
        lines.append(f"{finding.confidence:.2f}" if finding else "0.00")

        lines.extend(["", "Доказательная база:"])
        if finding and finding.evidence:
            lines.extend(f"- {item.description} (+{item.weight:.2f})" for item in finding.evidence)
        else:
            lines.append("- правила не собрали evidence")

        lines.extend(["", "Возможные причины:"])
        if finding and finding.assumptions:
            lines.extend(f"- {assumption}" for assumption in finding.assumptions)
        else:
            lines.append("- недостаточно сигналов для вероятных причин")

        lines.extend(["", "Рекомендуемые проверки:"])
        if finding and finding.recommended_checks:
            lines.extend(f"- {check}" for check in finding.recommended_checks)
        else:
            lines.append("- проверить traceback и шаги Allure")

        if summary.step_sequence and summary.step_sequence.nodes:
            lines.extend(["", "Последовательность шагов:"])
            lines.extend(
                f"{node.id}. {node.kind or 'step'}: {node.title} - {node.status}"
                for node in summary.step_sequence.nodes
            )

        lines.extend(["", "Сырые сигналы:"])
        if summary.raw_signals:
            visible = summary.raw_signals[: self._max_raw_signals]
            lines.extend(f"- {signal.describe()}" for signal in visible)
            hidden = len(summary.raw_signals) - len(visible)
            if hidden > 0:
                lines.append(f"- ... скрыто сигналов: {hidden}")
        else:
            lines.append("- сырые сигналы не собраны")

        lines.extend(["", "============================================================"])
        return "\n".join(lines)
