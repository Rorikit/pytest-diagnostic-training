from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from pytest_diagnostics.core.context import get_current_context
from pytest_diagnostics.core.models import DiagnosticFact, DiagnosticSignal, NetworkEvent, SignalSeverity
from pytest_diagnostics.utils.time import elapsed_ms, now_epoch, now_monotonic


class HttpxInstrumentation:
    """Optional httpx instrumentation with no hard dependency on httpx."""

    _installed = False
    _client_original: Callable[..., Any] | None = None
    _async_client_original: Callable[..., Any] | None = None

    def install(self) -> None:
        if self.__class__._installed:
            return
        try:
            import httpx
        except ImportError:
            return

        client_original = httpx.Client.request
        async_original = httpx.AsyncClient.request
        self.__class__._client_original = client_original
        self.__class__._async_client_original = async_original

        @wraps(client_original)
        def observed(client, method, url, *args, **kwargs):
            started = now_monotonic()
            try:
                response = client_original(client, method, url, *args, **kwargs)
            except Exception as exc:
                self._record(method, url, None, elapsed_ms(started), error=repr(exc))
                raise
            self._record(method, url, response.status_code, elapsed_ms(started), error=None)
            return response

        @wraps(async_original)
        async def observed_async(client, method, url, *args, **kwargs):
            started = now_monotonic()
            try:
                response = await async_original(client, method, url, *args, **kwargs)
            except Exception as exc:
                self._record(method, url, None, elapsed_ms(started), error=repr(exc))
                raise
            self._record(method, url, response.status_code, elapsed_ms(started), error=None)
            return response

        httpx.Client.request = observed
        httpx.AsyncClient.request = observed_async
        self.__class__._installed = True

    def uninstall(self) -> None:
        if not self.__class__._installed:
            return
        try:
            import httpx
        except ImportError:
            return
        if self.__class__._client_original is not None:
            httpx.Client.request = self.__class__._client_original
        if self.__class__._async_client_original is not None:
            httpx.AsyncClient.request = self.__class__._async_client_original
        self.__class__._client_original = None
        self.__class__._async_client_original = None
        self.__class__._installed = False

    def _record(self, method, url, status_code, duration_ms, *, error: str | None) -> None:
        context = get_current_context()
        if context is None:
            return
        event = NetworkEvent(
            library="httpx",
            method=str(method).upper(),
            url=str(url),
            status_code=status_code,
            elapsed_ms=duration_ms,
            error=error,
        )
        context.network_events.append(event)
        context.add_fact(
            DiagnosticFact(
                name="network.httpx",
                value={"method": event.method, "url": event.url, "status_code": status_code},
                source="httpx",
                timestamp=now_epoch(),
                metadata={"elapsed_ms": duration_ms, "error": error},
            )
        )
        if error or (status_code is not None and status_code >= 400):
            context.add_signal(
                DiagnosticSignal(
                    kind="network.http_error",
                    source="httpx",
                    message=error or f"{event.method} {event.url} вернул HTTP {status_code}",
                    severity=SignalSeverity.ERROR if error or status_code >= 500 else SignalSeverity.WARNING,
                    timestamp=now_epoch(),
                    data={
                        "library": "httpx",
                        "method": event.method,
                        "url": event.url,
                        "status_code": status_code,
                        "elapsed_ms": duration_ms,
                    },
                )
            )
