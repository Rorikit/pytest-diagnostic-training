from __future__ import annotations


def confidence_label(value: float) -> str:
    if value >= 0.75:
        return "высокая"
    if value >= 0.45:
        return "средняя"
    return "низкая"
