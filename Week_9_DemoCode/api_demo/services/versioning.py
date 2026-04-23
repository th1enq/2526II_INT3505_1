from flask import Request

from api_demo.config import DEFAULT_API_VERSION


def parse_version_from_header(value: str | None) -> int | None:
    if not value:
        return None

    normalized = value.strip().lower()
    if normalized in {"1", "v1"}:
        return 1
    if normalized in {"2", "v2"}:
        return 2

    if normalized.startswith("application/vnd.demo.v") and normalized.endswith("+json"):
        try:
            version_str = normalized.split(".v", maxsplit=1)[1].split("+", maxsplit=1)[0]
            return int(version_str)
        except (ValueError, IndexError):
            return None

    return None


def resolve_version(request: Request) -> int:
    query_version = request.args.get("version")
    if query_version:
        try:
            return int(query_version)
        except ValueError:
            return -1

    accept_version = parse_version_from_header(request.headers.get("Accept"))
    if accept_version is not None:
        return accept_version

    explicit_version = parse_version_from_header(request.headers.get("X-API-Version"))
    if explicit_version is not None:
        return explicit_version

    return DEFAULT_API_VERSION
