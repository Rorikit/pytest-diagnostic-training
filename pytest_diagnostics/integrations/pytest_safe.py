from __future__ import annotations

from typing import Any


def stash_key(name: str) -> str:
    return f"pytest_diagnostics.{name}"


def get_nodeid(item: Any) -> str:
    return str(item.nodeid)

