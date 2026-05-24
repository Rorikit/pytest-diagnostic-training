from __future__ import annotations

from pytest_diagnostics.core.models import DiagnosticResult
from pytest_diagnostics.output.formatter import confidence_label


class MarkdownSummaryBuilder:
    def build(self, result: DiagnosticResult) -> str:
        hypothesis = result.primary_hypothesis
        lines = [self._status_text(result.status), "", "Факты:"]
        if result.facts:
            for fact in result.facts[:12]:
                lines.append(f"* {self._fact_text(fact.name, fact.value)}")
        else:
            lines.append("* runtime-факты не собраны")

        lines.extend(["", "Вероятная область проблемы:"])
        lines.append(hypothesis.area if hypothesis else "Не определена")

        lines.extend(["", "Уверенность:"])
        lines.append(confidence_label(hypothesis.confidence) if hypothesis else "низкая")

        lines.extend(["", "Возможные причины:"])
        if hypothesis:
            lines.extend(f"* {cause}" for cause in hypothesis.possible_causes)
        else:
            lines.append("* собрано недостаточно диагностических сигналов")

        lines.extend(["", "Рекомендуемые проверки:"])
        if hypothesis:
            lines.extend(f"* {check}" for check in hypothesis.recommended_checks)
        else:
            lines.append("* проверить traceback, шаги Allure и runtime-логи")

        if hypothesis and hypothesis.evidence:
            lines.extend(["", "Основания для вывода:"])
            lines.extend(f"* {item}" for item in hypothesis.evidence)

        return "\n".join(lines)

    def _status_text(self, status: str) -> str:
        if status == "failed":
            return "УПАЛ"
        if status == "passed":
            return "ПРОШЕЛ"
        return status.upper()

    def _fact_text(self, name: str, value) -> str:
        if name == "allure.step.started":
            return f"стартовал allure.step: {value}"
        if name == "allure.step.finished" and isinstance(value, dict):
            return f"allure.step '{value.get('title')}' завершился со статусом {self._outcome_text(value.get('status'))}"
        if name.startswith("pytest.") and name.endswith(".outcome"):
            phase = name.split(".")[1]
            return f"pytest-фаза {self._phase_text(phase)} завершилась со статусом {self._outcome_text(value)}"
        if name.startswith("network."):
            method = value.get("method") if isinstance(value, dict) else None
            url = value.get("url") if isinstance(value, dict) else None
            status = value.get("status_code") if isinstance(value, dict) else None
            return f"{method} {url} вернул HTTP {status}"
        return f"{name}: {value}"

    def _phase_text(self, phase: str) -> str:
        return {
            "setup": "подготовки",
            "call": "выполнения",
            "teardown": "завершения",
        }.get(phase, phase)

    def _outcome_text(self, outcome) -> str:
        return {
            "passed": "успех",
            "failed": "ошибка",
            "skipped": "пропуск",
        }.get(str(outcome), str(outcome))
