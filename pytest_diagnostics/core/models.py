from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Mapping


class DiagnosticPhase(str, Enum):
    SETUP = "setup"
    CALL = "call"
    TEARDOWN = "teardown"
    UNKNOWN = "unknown"


class SignalSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class DiagnosticFact:
    """Observed runtime fact. Facts are evidence, not conclusions."""

    name: str
    value: Any
    source: str
    phase: str = DiagnosticPhase.UNKNOWN.value
    timestamp: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class DiagnosticSignal:
    """Normalized event emitted by collectors for later analysis."""

    kind: str
    source: str
    message: str
    severity: SignalSeverity = SignalSeverity.INFO
    phase: str = DiagnosticPhase.UNKNOWN.value
    timestamp: float | None = None
    data: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeReport:
    phase: str
    outcome: str
    duration: float | None = None
    longrepr: str | None = None


@dataclass(slots=True)
class NetworkEvent:
    library: str
    method: str
    url: str
    status_code: int | None
    elapsed_ms: float
    error: str | None = None


@dataclass(slots=True)
class RuntimeException:
    exc_type: str
    message: str
    phase: str
    traceback: str | None = None


@dataclass(slots=True)
class RuntimeStep:
    title: str
    status: str
    started_at: float
    finished_at: float | None = None
    duration_ms: float | None = None
    error: str | None = None
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TestDiagnosticContext:
    __test__: ClassVar[bool] = False

    nodeid: str
    started_at: float
    facts: list[DiagnosticFact] = field(default_factory=list)
    signals: list[DiagnosticSignal] = field(default_factory=list)
    steps: list[RuntimeStep] = field(default_factory=list)
    exceptions: list[RuntimeException] = field(default_factory=list)
    reports: list[RuntimeReport] = field(default_factory=list)
    network_events: list[NetworkEvent] = field(default_factory=list)
    attachments: list[Mapping[str, Any]] = field(default_factory=list)
    finished_at: float | None = None

    def add_fact(self, fact: DiagnosticFact) -> None:
        self.facts.append(fact)

    def add_signal(self, signal: DiagnosticSignal) -> None:
        self.signals.append(signal)

    def failed(self) -> bool:
        return any(report.outcome == "failed" for report in self.reports)
