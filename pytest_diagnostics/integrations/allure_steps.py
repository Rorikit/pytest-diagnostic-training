from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable

from pytest_diagnostics.core.context import get_current_context
from pytest_diagnostics.core.models import (
    DiagnosticFact,
    DiagnosticSignal,
    RuntimeStep,
    SignalSeverity,
)
from pytest_diagnostics.utils.time import elapsed_ms, now_epoch, now_monotonic


@dataclass(slots=True, frozen=True)
class StepSemantic:
    tags: tuple[str, ...] = ()
    http_status: int | None = None
    endpoint: str | None = None
    confidence_hint: float = 0.0


class StepSemanticExtractor:
    _tag_patterns = (
        ("auth", re.compile(r"\b(login|auth|token|session|401|403|роль|права|сесс)", re.I)),
        ("api", re.compile(r"\b(api|http|request|response|endpoint|GET|POST|PUT|PATCH|DELETE|redfish)\b", re.I)),
        ("ui", re.compile(r"\b(ui|web|page|browser|frontend|форма|страниц|интерфейс)\b", re.I)),
        ("compare", re.compile(r"\b(compare|assert|equal|match|сравн|провер|ожидаем)", re.I)),
        ("timeout", re.compile(r"\b(timeout|timed out|wait|ожидан|таймаут)\b", re.I)),
        ("dependency", re.compile(r"\b(dependency|service|broker|queue|db|redis|kafka|connect|соедин|зависим)", re.I)),
        ("cache", re.compile(r"\b(cache|кэш|stale|устар)", re.I)),
    )
    _status_pattern = re.compile(r"(?:HTTP\s*)?(?P<status>[1-5]\d\d)")
    _endpoint_pattern = re.compile(r"\b(?:GET|POST|PUT|PATCH|DELETE)\s+(?P<endpoint>/[^\s]+)", re.I)

    def extract(self, title: str) -> StepSemantic:
        tags = tuple(tag for tag, pattern in self._tag_patterns if pattern.search(title))
        status_match = self._status_pattern.search(title)
        endpoint_match = self._endpoint_pattern.search(title)
        confidence_hint = min(0.25, len(tags) * 0.04)
        return StepSemantic(
            tags=tags,
            http_status=int(status_match.group("status")) if status_match else None,
            endpoint=endpoint_match.group("endpoint") if endpoint_match else None,
            confidence_hint=confidence_hint,
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
        self._extractor = StepSemanticExtractor()

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
            semantic = self._extractor.extract(str(title))
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
                    kind="allure.step",
                    source="allure",
                    message=self.title,
                    severity=SignalSeverity.INFO,
                    timestamp=observed.started_epoch,
                    data={
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
                    kind="allure.step_failed",
                    source="allure",
                    message=step.title,
                    severity=SignalSeverity.ERROR,
                    timestamp=step.finished_at,
                    data={
                        "title": step.title,
                        "tags": step.tags,
                        "error": error,
                        "http_status": observed.semantic.http_status,
                        "endpoint": observed.semantic.endpoint,
                    },
                )
            )
