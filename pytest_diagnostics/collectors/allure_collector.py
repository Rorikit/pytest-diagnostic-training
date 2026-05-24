from __future__ import annotations

from pytest_diagnostics.collectors.base import RuntimeCollector
from pytest_diagnostics.integrations.allure_steps import AllureStepInstrumentation


class AllureCollector(RuntimeCollector):
    name = "allure"

    def __init__(self) -> None:
        self._instrumentation = AllureStepInstrumentation()

    def configure(self, config) -> None:
        self._instrumentation.install()

    def unconfigure(self) -> None:
        self._instrumentation.uninstall()
