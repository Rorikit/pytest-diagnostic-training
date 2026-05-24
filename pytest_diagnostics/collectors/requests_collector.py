from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.integrations.requests_patch import RequestsInstrumentation


class RequestsCollector(RuntimeCollector):
    name = "requests"

    def __init__(self) -> None:
        self._instrumentation = RequestsInstrumentation()

    def configure(self, config) -> None:
        self._instrumentation.install()

    def unconfigure(self) -> None:
        self._instrumentation.uninstall()

