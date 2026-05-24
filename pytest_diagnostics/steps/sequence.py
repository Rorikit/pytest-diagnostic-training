from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pytest_diagnostics.core.models import RuntimeStep, TestDiagnosticContext
from pytest_diagnostics.steps.semantics import StepSemanticAnalyzer


@dataclass(slots=True, frozen=True)
class StepNode:
    id: int
    title: str
    kind: str | None
    status: str
    started_at: float
    finished_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class StepSequence:
    nodes: list[StepNode]

    @property
    def failed_step(self) -> StepNode | None:
        for node in self.nodes:
            if node.status == "failed":
                return node
        return None

    def previous_successful_steps(self) -> list[StepNode]:
        failed = self.failed_step
        if failed is None:
            return [node for node in self.nodes if node.status == "passed"]
        return [node for node in self.nodes if node.id < failed.id and node.status == "passed"]


class StepSequenceBuilder:
    def __init__(self, analyzer: StepSemanticAnalyzer | None = None) -> None:
        self._analyzer = analyzer or StepSemanticAnalyzer()

    def build(self, context: TestDiagnosticContext) -> StepSequence:
        return StepSequence(
            nodes=[self._node(index, step) for index, step in enumerate(context.steps, start=1)]
        )

    def _node(self, index: int, step: RuntimeStep) -> StepNode:
        semantic = self._analyzer.analyze(step.title)
        metadata = dict(step.metadata)
        metadata.update(semantic.metadata)
        metadata["tags"] = semantic.tags
        return StepNode(
            id=index,
            title=step.title,
            kind=semantic.kind,
            status=step.status,
            started_at=step.started_at,
            finished_at=step.finished_at,
            metadata=metadata,
        )

