from __future__ import annotations

import traceback
from types import TracebackType


def format_exception(
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    tb: TracebackType | None,
) -> str | None:
    if exc_type is None or exc is None:
        return None
    return "".join(traceback.format_exception(exc_type, exc, tb))


def compact_traceback(text: str | None, *, max_lines: int = 12) -> str | None:
    if not text:
        return None
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return "\n".join(lines)
    head = lines[: max_lines // 2]
    tail = lines[-(max_lines // 2) :]
    return "\n".join([*head, "...", *tail])

