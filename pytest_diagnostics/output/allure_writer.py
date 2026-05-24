from __future__ import annotations

import json

from pytest_diagnostics.core.models import DiagnosticResult
from pytest_diagnostics.output.summary_builder import MarkdownSummaryBuilder
from pytest_diagnostics.utils.serialization import to_jsonable


class AllureDiagnosticWriter:
    def __init__(self, include_snapshot: bool = True, include_description: bool = True) -> None:
        self._summary_builder = MarkdownSummaryBuilder()
        self._include_snapshot = include_snapshot
        self._include_description = include_description

    def write(self, result: DiagnosticResult) -> str:
        summary = self._summary_builder.build(result)
        try:
            import allure
        except ImportError:
            return summary

        if self._include_description:
            self._write_description(allure, summary)

        try:
            allure.attach(
                summary,
                name="Диагностическое резюме",
                attachment_type=self._attachment_type(allure, "MARKDOWN", fallback="TEXT"),
            )
        except Exception:
            return summary

        if self._include_snapshot:
            snapshot = json.dumps(to_jsonable(result), ensure_ascii=False, indent=2)
            try:
                allure.attach(
                    snapshot,
                    name="Runtime-снимок диагностики",
                    attachment_type=self._attachment_type(allure, "JSON", fallback="TEXT"),
                )
            except Exception:
                return summary
        return summary

    def _write_description(self, allure_module, summary: str) -> None:
        dynamic = getattr(allure_module, "dynamic", None)
        description = getattr(dynamic, "description", None) if dynamic is not None else None
        if description is None:
            return
        try:
            description(summary)
        except Exception:
            return

    def _attachment_type(self, allure_module, name: str, *, fallback: str):
        attachment_type = getattr(allure_module, "attachment_type", None)
        if attachment_type is None:
            return None
        return getattr(attachment_type, name, getattr(attachment_type, fallback, None))
