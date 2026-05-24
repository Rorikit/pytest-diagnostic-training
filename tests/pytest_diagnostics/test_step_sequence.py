from pytest_diagnostics.core.models import RuntimeStep, TestDiagnosticContext
from pytest_diagnostics.steps.sequence import StepSequenceBuilder


def test_step_sequence_builds_ordered_nodes_and_failed_step():
    context = TestDiagnosticContext(nodeid="tests/test_flow.py::test_case", started_at=0)
    context.steps.extend(
        [
            RuntimeStep(title="Логин под admin-сессией", status="passed", started_at=1),
            RuntimeStep(title="GET /redfish/v1/Chassis", status="passed", started_at=2),
            RuntimeStep(title="Получение Members из Web UI", status="passed", started_at=3),
            RuntimeStep(title="Сравнение API Members и UI Members", status="failed", started_at=4),
        ]
    )

    sequence = StepSequenceBuilder().build(context)

    assert [node.id for node in sequence.nodes] == [1, 2, 3, 4]
    assert sequence.nodes[0].kind == "auth"
    assert sequence.nodes[1].kind == "api_request"
    assert sequence.failed_step is not None
    assert sequence.failed_step.title == "Сравнение API Members и UI Members"
    assert [node.title for node in sequence.previous_successful_steps()] == [
        "Логин под admin-сессией",
        "GET /redfish/v1/Chassis",
        "Получение Members из Web UI",
    ]
