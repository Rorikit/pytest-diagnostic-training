from __future__ import annotations

import re

HTTP_REQUEST_RE = re.compile(r"\b(?P<method>GET|POST|PUT|PATCH|DELETE)\s+(?P<endpoint>/[^\s]+)", re.I)
HTTP_STATUS_RE = re.compile(r"(?:HTTP\s*|status(?:_code)?\D+|вернул\D+)(?P<status>[1-5]\d\d)\b", re.I)
ROLE_RE = re.compile(r"\b(?P<role>admin|readonly|user|operator|viewer|guest)[-\s]*(?:сесс|session)?", re.I)
DATA_ENTITY_RE = re.compile(r"\b(?P<entity>members|users|orders|chassis|sessions)\b", re.I)

AUTH_RE = re.compile(r"\b(login|auth|token|session|логин|сесс|роль|права)\b", re.I)
UI_RE = re.compile(r"\b(ui|web|page|browser|frontend|страниц|интерфейс)\b", re.I)
COMPARISON_RE = re.compile(r"(compare|assert|equal|match|сравн\w*|ожидаем\w*)", re.I)
TIMEOUT_RE = re.compile(r"\b(timeout|timed out|wait|ожидан|таймаут)\b", re.I)
DEPENDENCY_RE = re.compile(r"\b(dependency|service|broker|queue|db|redis|kafka|connect|соедин|зависим)\b", re.I)
CACHE_RE = re.compile(r"\b(cache|кэш|stale|устар)\b", re.I)


def normalize_entity(value: str) -> str:
    return value.lower()


def endpoint_domain(endpoint: str) -> str | None:
    parts = [part for part in endpoint.strip("/").split("/") if part]
    if not parts:
        return None
    if parts[0].lower() == "redfish":
        return "redfish"
    return parts[0].lower()


def endpoint_resource(endpoint: str) -> str | None:
    parts = [part for part in endpoint.strip("/").split("/") if part]
    if not parts:
        return None
    return parts[-1].lower()
