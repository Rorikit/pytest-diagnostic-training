from pytest_diagnostics.core.models import DiagnosticFact, DiagnosticHypothesis, DiagnosticResult
from pytest_diagnostics.output.summary_builder import MarkdownSummaryBuilder


def test_summary_uses_required_diagnostic_sections():
    result = DiagnosticResult(
        nodeid="tests/test_example.py::test_failure",
        status="failed",
        facts=(DiagnosticFact(name="pytest.call.outcome", value="failed", source="pytest"),),
        signals=(),
        hypotheses=(
            DiagnosticHypothesis(
                area="Синхронизация данных / UI cache",
                confidence=0.6,
                possible_causes=("устаревший UI cache", "задержка async-обновления"),
                recommended_checks=("проверить network requests", "сравнить timestamps"),
                evidence=("зафиксирован AssertionError",),
                rule_id="test",
            ),
        ),
    )

    summary = MarkdownSummaryBuilder().build(result)

    assert "УПАЛ" in summary
    assert "Факты:" in summary
    assert "Вероятная область проблемы:" in summary
    assert "Уверенность:" in summary
    assert "Возможные причины:" in summary
    assert "Рекомендуемые проверки:" in summary
    assert "Синхронизация данных / UI cache" in summary
