from __future__ import annotations

from abc import ABC, abstractmethod

from pytest_diagnostics.diagnostics.models import DiagnosticEvidence, DiagnosticFinding
from pytest_diagnostics.signals.models import DiagnosticSignal


class DiagnosticRule(ABC):
    name: str

    @abstractmethod
    def match(self, signals: list[DiagnosticSignal]) -> DiagnosticFinding | None:
        """Return a finding when enough supporting signals exist."""


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def confidence_from(evidence: list[DiagnosticEvidence]) -> float:
    return clamp_confidence(sum(item.weight for item in evidence))


def has_signal(signals: list[DiagnosticSignal], signal_type: str, value: object | None = None) -> bool:
    for signal in signals:
        if signal.type != signal_type:
            continue
        if value is None or signal.value == value:
            return True
    return False


def matching_signal(
    signals: list[DiagnosticSignal],
    signal_type: str,
    value: object | None = None,
) -> DiagnosticSignal | None:
    for signal in signals:
        if signal.type != signal_type:
            continue
        if value is None or signal.value == value:
            return signal
    return None


def first_signal(signals: list[DiagnosticSignal], signal_type: str) -> DiagnosticSignal | None:
    for signal in signals:
        if signal.type == signal_type:
            return signal
    return None


def signal_values(signals: list[DiagnosticSignal], signal_type: str) -> list[object]:
    return [signal.value for signal in signals if signal.type == signal_type]


def signal_text(signals: list[DiagnosticSignal], signal_type: str) -> str:
    values = [str(signal.value) for signal in signals if signal.type == signal_type]
    return "\n".join(values).lower()
