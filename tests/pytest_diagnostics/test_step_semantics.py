from pytest_diagnostics.steps.semantics import StepSemanticAnalyzer


def test_step_semantics_extract_api_request():
    semantic = StepSemanticAnalyzer().analyze("GET /redfish/v1/Chassis")

    assert semantic.kind == "api_request"
    assert semantic.metadata["http_method"] == "GET"
    assert semantic.metadata["endpoint"] == "/redfish/v1/Chassis"
    assert semantic.metadata["domain"] == "redfish"
    assert semantic.metadata["resource"] == "chassis"


def test_step_semantics_extract_auth_role():
    semantic = StepSemanticAnalyzer().analyze("Логин под admin-сессией")

    assert semantic.kind == "auth"
    assert semantic.metadata["role"] == "admin"


def test_step_semantics_extract_ui_data_entity():
    semantic = StepSemanticAnalyzer().analyze("Получение Members из Web UI")

    assert semantic.kind == "ui"
    assert semantic.metadata["data_entity"] == "members"


def test_step_semantics_extract_comparison_sources_and_entity():
    semantic = StepSemanticAnalyzer().analyze("Сравнение API Members и UI Members")

    assert semantic.kind == "comparison"
    assert semantic.metadata["compared_sources"] == ("api", "ui")
    assert semantic.metadata["data_entity"] == "members"
