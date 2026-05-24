from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable

from pytest_diagnostics.core.context import get_current_context
from pytest_diagnostics.core.models import (
    DiagnosticFact,
    RuntimeStep,
)
from pytest_diagnostics.signals.models import DiagnosticSignal
from pytest_diagnostics.steps.semantics import StepSemanticAnalyzer
from pytest_diagnostics.utils.time import elapsed_ms, now_epoch, now_monotonic


@dataclass(slots=True, frozen=True)
class StepSemantic:
    tags: tuple[str, ...] = ()
    http_status: int | None = None
    endpoint: str | None = None
    confidence_hint: float = 0.0


class AllureStepSemanticAdapter:
    def __init__(self, analyzer: StepSemanticAnalyzer | None = None) -> None:
        self._analyzer = analyzer or StepSemanticAnalyzer()

    def extract(self, title: str) -> StepSemantic:
        info = self._analyzer.analyze(title)
        return StepSemantic(
            tags=info.tags,
            http_status=info.metadata.get("http_status"),
            endpoint=info.metadata.get("endpoint"),
            confidence_hint=min(0.25, len(info.tags) * 0.04),
        )


@dataclass(slots=True)
class _ObservedStep:
    title: str
    started_monotonic: float
    started_epoch: float
    semantic: StepSemantic


class AllureStepInstrumentation:
    """Wraps public allure.step and records step diagnostics passively."""

    _installed = False
    _original_step: Callable[..., Any] | None = None

    def __init__(self) -> None:
        self._semantic_adapter = AllureStepSemanticAdapter()

    def install(self) -> None:
        if self.__class__._installed:
            return
        try:
            import allure
        except ImportError:
            return

        original_step = allure.step
        self.__class__._original_step = original_step

        @wraps(original_step)
        def observed_step(title):
            original_context = original_step(title)
            semantic = self._semantic_adapter.extract(str(title))
            return _StepContextProxy(str(title), original_context, semantic, original_step)

        allure.step = observed_step
        self.__class__._installed = True

    def uninstall(self) -> None:
        if not self.__class__._installed or self.__class__._original_step is None:
            return
        try:
            import allure
        except ImportError:
            return
        allure.step = self.__class__._original_step
        self.__class__._original_step = None
        self.__class__._installed = False


@dataclass(slots=True)
class _StepContextProxy:
    title: str
    original_context: Any
    semantic: StepSemantic
    step_factory: Callable[[str], Any]
    _observed: _ObservedStep | None = field(default=None, init=False)

    def __enter__(self):
        self._observed = self._start_step()
        return self.original_context.__enter__()

    def __exit__(self, exc_type, exc, tb):
        try:
            return self.original_context.__exit__(exc_type, exc, tb)
        finally:
            self._finish_step(exc_type, exc)

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            context = _StepContextProxy(
                self.title,
                self.step_factory(self.title),
                self.semantic,
                self.step_factory,
            )
            with context:
                return func(*args, **kwargs)

        return wrapped

    def _start_step(self) -> _ObservedStep:
        observed = _ObservedStep(
            title=self.title,
            started_monotonic=now_monotonic(),
            started_epoch=now_epoch(),
            semantic=self.semantic,
        )
        context = get_current_context()
        if context is not None:
            context.add_fact(
                DiagnosticFact(
                    name="allure.step.started",
                    value=self.title,
                    source="allure",
                    timestamp=observed.started_epoch,
                    metadata={
                        "tags": self.semantic.tags,
                        "http_status": self.semantic.http_status,
                        "endpoint": self.semantic.endpoint,
                    },
                )
            )
            context.add_signal(
                DiagnosticSignal(
                    type="allure_step_started",
                    value=self.title,
                    source="allure",
                    metadata={
                        "title": self.title,
                        "tags": self.semantic.tags,
                        "http_status": self.semantic.http_status,
                        "endpoint": self.semantic.endpoint,
                        "confidence_hint": self.semantic.confidence_hint,
                    },
                )
            )
        return observed

    def _finish_step(self, exc_type, exc) -> None:
        observed = self._observed
        if observed is None:
            return
        context = get_current_context()
        if context is None:
            return
        duration = elapsed_ms(observed.started_monotonic)
        status = "failed" if exc_type is not None else "passed"
        error = f"{exc_type.__name__}: {exc}" if exc_type is not None else None
        step = RuntimeStep(
            title=observed.title,
            status=status,
            started_at=observed.started_epoch,
            finished_at=now_epoch(),
            duration_ms=duration,
            error=error,
            tags=observed.semantic.tags,
            metadata={
                "http_status": observed.semantic.http_status,
                "endpoint": observed.semantic.endpoint,
                "confidence_hint": observed.semantic.confidence_hint,
            },
        )
        context.steps.append(step)
        context.add_fact(
            DiagnosticFact(
                name="allure.step.finished",
                value={"title": step.title, "status": step.status},
                source="allure",
                timestamp=step.finished_at,
                metadata={
                    "duration_ms": duration,
                    "tags": step.tags,
                    "http_status": observed.semantic.http_status,
                    "endpoint": observed.semantic.endpoint,
                    "error": error,
                },
            )
        )
        if error is not None:
            context.add_signal(
                DiagnosticSignal(
                    type="allure_step_failed",
                    value=step.title,
                    source="allure",
                    severity="error",
                    metadata={
                        "title": step.title,
                        "tags": step.tags,
                        "error": error,
                        "http_status": observed.semantic.http_status,
                        "endpoint": observed.semantic.endpoint,
                    },
                )
            )
