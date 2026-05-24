from pytest_diagnostics.diagnostics.formatter import TextDiagnosticFormatter
from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding, DiagnosticSummary
from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.steps.sequence import StepNode, StepSequence


def test_formatter_outputs_facts_assumptions_and_raw_signals():
    summary = DiagnosticSummary(
        findings=[
            DiagnosticFinding(
                area="Сравнение данных",
                title="Несовпадение ожидаемого и фактического результата",
                explanation="Тест завершился с AssertionError.",
                confidence=0.45,
                facts=["тест завершился с AssertionError"],
                assumptions=["фактические и ожидаемые значения отличаются"],
                recommended_checks=["проверить сравниваемые значения"],
                evidence=[DiagnosticEvidence("Обнаружен AssertionError", 0.35)],
                rule_name="assertion_mismatch",
            )
        ],
        raw_signals=[
            DiagnosticSignal(type=f"signal_{index}", value=index, source="test")
            for index in range(15)
        ],
        step_sequence=StepSequence(
            nodes=[
                StepNode(id=1, title="Логин под admin-сессией", kind="auth", status="passed", started_at=0),
                StepNode(id=2, title="Сравнение API Members и UI Members", kind="comparison", status="failed", started_at=1),
            ]
        ),
    )

    text = TextDiagnosticFormatter().format(summary)

    assert "PYTEST DIAGNOSTICS" in text
    assert "Известные факты:" in text
    assert "Наиболее вероятная область:" in text
    assert "Сравнение данных" in text
    assert "Доказательная база:" in text
    assert "Обнаружен AssertionError (+0.35)" in text
    assert "Последовательность шагов:" in text
    assert "1. auth: Логин под admin-сессией - passed" in text
    assert "... скрыто сигналов: 3" in text
