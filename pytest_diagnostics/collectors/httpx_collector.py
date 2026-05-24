from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.integrations.httpx_hooks import HttpxInstrumentation


class HttpxCollector(RuntimeCollector):
    name = "httpx"

    def __init__(self) -> None:
        self._instrumentation = HttpxInstrumentation()

    def configure(self, config) -> None:
        self._instrumentation.install()

    def unconfigure(self) -> None:
        self._instrumentation.uninstall()

