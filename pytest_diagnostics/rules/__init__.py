from pytest_diagnostics.rules.api import ServerErrorRule
from pytest_diagnostics.rules.assertions import AssertionMismatchRule, MissingFieldRule
from pytest_diagnostics.rules.auth import ForbiddenRule, UnauthorizedRule
from pytest_diagnostics.rules.infra import ConnectionRule, TimeoutRule


def default_rules():
    return [
        ForbiddenRule(),
        UnauthorizedRule(),
        ServerErrorRule(),
        MissingFieldRule(),
        TimeoutRule(),
        ConnectionRule(),
        AssertionMismatchRule(),
    ]


__all__ = [
    "AssertionMismatchRule",
    "ConnectionRule",
    "ForbiddenRule",
    "MissingFieldRule",
    "ServerErrorRule",
    "TimeoutRule",
    "UnauthorizedRule",
    "default_rules",
]
