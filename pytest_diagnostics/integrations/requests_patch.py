from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from pytest_diagnostics.core.context import get_current_context
from pytest_diagnostics.core.models import DiagnosticFact, DiagnosticSignal, NetworkEvent, SignalSeverity
from pytest_diagnostics.utils.time import elapsed_ms, now_epoch, now_monotonic


class RequestsInstrumentation:
    """Idempotent requests instrumentation around the public Session API."""

    _installed = False
    _original: Callable[..., Any] | None = None

    def install(self) -> None:
        if self.__class__._installed:
            return
        try:
            import requests
        except ImportError:
            return

        original = requests.sessions.Session.request
        self.__class__._original = original

        @wraps(original)
        def observed(session, method, url, **kwargs):
            started = now_monotonic()
            try:
                response = original(session, method, url, **kwargs)
            except Exception as exc:
                self._record(method, url, None, elapsed_ms(started), error=repr(exc))
                raise
            self._record(
                method,
                url,
                getattr(response, "status_code", None),
                elapsed_ms(started),
                error=None,
            )
            return response

        requests.sessions.Session.request = observed
        self.__class__._installed = True

    def uninstall(self) -> None:
        if not self.__class__._installed or self.__class__._original is None:
            return
        try:
            import requests
        except ImportError:
            return
        requests.sessions.Session.request = self.__class__._original
        self.__class__._original = None
        self.__class__._installed = False

    def _record(
        self,
        method: str,
        url: str,
        status_code: int | None,
        duration_ms: float,
        *,
        error: str | None,
    ) -> None:
        context = get_current_context()
        if context is None:
            return
        event = NetworkEvent(
            library="requests",
            method=method.upper(),
            url=str(url),
            status_code=status_code,
            elapsed_ms=duration_ms,
            error=error,
        )
        context.network_events.append(event)
        context.add_fact(
            DiagnosticFact(
                name="network.requests",
                value={"method": event.method, "url": event.url, "status_code": status_code},
                source="requests",
                timestamp=now_epoch(),
                metadata={"elapsed_ms": duration_ms, "error": error},
            )
        )
        if error or (status_code is not None and status_code >= 400):
            context.add_signal(
                DiagnosticSignal(
                    kind="network.http_error",
                    source="requests",
                    message=error or f"{event.method} {event.url} вернул HTTP {status_code}",
                    severity=SignalSeverity.ERROR if error or status_code >= 500 else SignalSeverity.WARNING,
                    timestamp=now_epoch(),
                    data={
                        "library": "requests",
                        "method": event.method,
                        "url": event.url,
                        "status_code": status_code,
                        "elapsed_ms": duration_ms,
                    },
                )
            )
