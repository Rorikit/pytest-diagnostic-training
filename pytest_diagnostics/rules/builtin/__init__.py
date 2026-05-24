from pytest_diagnostics.rules.builtin.assertion import AssertionFailureRule
from pytest_diagnostics.rules.builtin.allure_steps import AllureStepCorrelationRule
from pytest_diagnostics.rules.builtin.dependency import DependencyFailureRule
from pytest_diagnostics.rules.builtin.fallback import FallbackFailureRule
from pytest_diagnostics.rules.builtin.http import HttpStatusRule
from pytest_diagnostics.rules.builtin.timeout import TimeoutRule


def default_rules():
    return [
        AllureStepCorrelationRule(),
        DependencyFailureRule(),
        HttpStatusRule(),
        TimeoutRule(),
        AssertionFailureRule(),
        FallbackFailureRule(),
    ]
