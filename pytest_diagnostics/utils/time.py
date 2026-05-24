from __future__ import annotations

from time import monotonic, time


def now_epoch() -> float:
    return time()


def now_monotonic() -> float:
    return monotonic()


def elapsed_ms(start: float, end: float | None = None) -> float:
    return round(((end if end is not None else monotonic()) - start) * 1000, 3)

