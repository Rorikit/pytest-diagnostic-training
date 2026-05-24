from pytest_diagnostics.core.models import (
    DiagnosticSignal,
    NetworkEvent,
    RuntimeException,
    RuntimeReport,
    SignalSeverity,
    TestDiagnosticContext,
)
from pytest_diagnostics.rules.builtin import default_rules
from pytest_diagnostics.rules.engine import RuleEngine


def failed_context(nodeid: str = "tests/test_mock.py::test_case") -> TestDiagnosticContext:
    context = TestDiagnosticContext(nodeid=nodeid, started_at=0)
    context.reports.append(RuntimeReport(phase="call", outcome="failed"))
    return context


def analyze(context: TestDiagnosticContext):
    result = RuleEngine(default_rules()).analyze(context)
    assert result.primary_hypothesis is not None
    return result.primary_hypothesis


def test_backend_500_mock_data_points_to_backend_service_failure():
    context = failed_context()
    context.network_events.append(
        NetworkEvent(
            library="requests",
            method="POST",
            url="https://api.test/orders",
            status_code=500,
            elapsed_ms=40.0,
        )
    )

    hypothesis = analyze(context)

    assert hypothesis.area == "Ошибка backend-сервиса"
    assert hypothesis.confidence == 0.75
    assert "backend-логи" in " ".join(hypothesis.recommended_checks)


def test_404_mock_data_points_to_missing_resource_or_route():
    context = failed_context()
    context.network_events.append(
        NetworkEvent(
            library="httpx",
            method="GET",
            url="https://api.test/users/unknown",
            status_code=404,
            elapsed_ms=18.0,
        )
    )

    hypothesis = analyze(context)

    assert hypothesis.area == "Доступность endpoint или ресурса"
    assert hypothesis.confidence == 0.7
    assert any("base URL" in check for check in hypothesis.recommended_checks)


def test_transport_error_mock_data_points_to_external_dependency():
    context = failed_context()
    context.network_events.append(
        NetworkEvent(
            library="requests",
            method="GET",
            url="https://dependency.test/health",
            status_code=None,
            elapsed_ms=250.0,
            error="ConnectionError('name resolution failed')",
        )
    )

    hypothesis = analyze(context)

    assert hypothesis.area == "Внешняя зависимость или сетевой транспорт"
    assert hypothesis.confidence == 0.7
    assert any("DNS" in cause for cause in hypothesis.possible_causes)


def test_timeout_mock_data_uses_exception_and_timing_signals():
    context = failed_context()
    context.exceptions.append(
        RuntimeException(
            exc_type="TimeoutError",
            message="operation timed out after 30 seconds",
            phase="call",
        )
    )
    context.signals.append(
        DiagnosticSignal(
            kind="timing.slow_phase",
            source="timing",
            message="pytest-фаза call заняла 30.000s",
            severity=SignalSeverity.WARNING,
            phase="call",
        )
    )

    hypothesis = analyze(context)

    assert hypothesis.area == "Timeout или медленный ответ сервиса"
    assert hypothesis.confidence == 0.65
    assert any("timeout" in check.lower() for check in hypothesis.recommended_checks)


def test_failed_context_without_specific_signals_uses_fallback_rule():
    context = failed_context()
    context.exceptions.append(
        RuntimeException(
            exc_type="ValueError",
            message="unexpected value",
            phase="call",
        )
    )

    hypothesis = analyze(context)

    assert hypothesis.area == "Неизвестная область падения"
    assert hypothesis.confidence == 0.25
    assert hypothesis.rule_id == "builtin.fallback"
