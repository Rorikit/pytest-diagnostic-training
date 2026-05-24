from pytest_diagnostics.engine.matcher import DiagnosticMatcher
from pytest_diagnostics.rules import default_rules
from pytest_diagnostics.signals.models import DiagnosticSignal


def analyze(signals: list[DiagnosticSignal]):
    summary = DiagnosticMatcher(default_rules()).match(signals)
    assert summary.top_finding is not None
    return summary.top_finding


def test_missing_field_rule_matches_key_error():
    finding = analyze([DiagnosticSignal(type="exception_type", value="KeyError", source="pytest")])

    assert finding.area == "Данные/схема"
    assert finding.confidence == 0.55
    assert "ожидаемое поле отсутствует" in finding.assumptions


def test_missing_field_rule_confidence_grows_in_api_request_context():
    finding = analyze(
        [
            DiagnosticSignal(type="exception_type", value="KeyError", source="pytest"),
            DiagnosticSignal(type="step_kind", value="api_request", source="step_semantics"),
        ]
    )

    assert finding.area == "Данные/схема"
    assert finding.confidence == 0.7


def test_unauthorized_rule_matches_401_message():
    finding = analyze(
        [DiagnosticSignal(type="exception_message", value="GET /me returned 401 Unauthorized", source="pytest")]
    )

    assert finding.area == "Аутентификация"
    assert finding.confidence == 0.4


def test_unauthorized_rule_prefers_http_status_signal():
    finding = analyze([DiagnosticSignal(type="http_status", value=401, source="step_semantics")])

    assert finding.area == "Аутентификация"
    assert finding.confidence == 0.65


def test_forbidden_rule_matches_insufficient_permissions():
    finding = analyze(
        [
            DiagnosticSignal(
                type="exception_message",
                value="Forbidden: insufficient permissions for endpoint",
                source="pytest",
            )
        ]
    )

    assert finding.area == "Права доступа"
    assert finding.confidence == 0.4


def test_forbidden_rule_prefers_http_status_signal():
    finding = analyze([DiagnosticSignal(type="http_status", value=403, source="step_semantics")])

    assert finding.area == "Права доступа"
    assert finding.confidence == 0.65


def test_timeout_rule_matches_timeout_signal():
    finding = analyze([DiagnosticSignal(type="exception_message", value="operation timed out", source="pytest")])

    assert finding.area == "Timeout/доступность сервиса"
    assert finding.confidence == 0.6


def test_connection_rule_matches_mock_redis_connection_failure():
    finding = analyze(
        [
            DiagnosticSignal(
                type="step_error",
                value="ConnectionError: Redis mock unavailable: connection refused",
                source="allure",
            )
        ]
    )

    assert finding.area == "Инфраструктура/сеть"
    assert finding.confidence == 0.6


def test_server_error_rule_matches_http_status_signal():
    finding = analyze([DiagnosticSignal(type="http_status", value=500, source="allure_step")])

    assert finding.area == "API/backend"
    assert finding.confidence == 0.65
