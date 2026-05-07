import json
import logging
import time
import uuid
from typing import Callable

from flask import Flask, Response, g, has_request_context, request
from pythonjsonlogger import jsonlogger
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


def setup_logging(app: Flask) -> None:
    log_level = getattr(logging, (app.config.get("LOG_LEVEL") or "INFO").upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(log_level)

    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler()
    fmt = app.config.get("LOG_FORMAT", "json")
    if fmt == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(trace_id)s %(span_id)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s request_id=%(request_id)s trace_id=%(trace_id)s"
        )

    handler.addFilter(RequestContextFilter())
    handler.setFormatter(formatter)
    root.addHandler(handler)


def _get_trace_ids() -> tuple[str | None, str | None]:
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        if not ctx or not ctx.is_valid:
            return None, None
        trace_id = format(ctx.trace_id, "032x")
        span_id = format(ctx.span_id, "016x")
        return trace_id, span_id
    except Exception:
        return None, None


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(g, "request_id", None) if has_request_context() else None
        trace_id, span_id = _get_trace_ids()
        record.trace_id = trace_id
        record.span_id = span_id
        return True


def init_request_context(app: Flask) -> None:
    @app.before_request
    def _before_request() -> None:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_id = request_id
        g._start_time = time.perf_counter()

    @app.after_request
    def _after_request(resp: Response) -> Response:
        resp.headers["X-Request-ID"] = getattr(g, "request_id", "")
        return resp


def init_audit_logging(app: Flask) -> None:
    audit_logger = logging.getLogger("audit")
    audit_logger.propagate = True

    @app.after_request
    def _audit(resp: Response) -> Response:
        try:
            start = getattr(g, "_start_time", None)
            latency = (time.perf_counter() - start) if start else None
            payload = {
                "event": "http_request",
                "request_id": getattr(g, "request_id", None),
                "method": request.method,
                "path": request.path,
                "status": resp.status_code,
                "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
                "user_agent": request.headers.get("User-Agent"),
                "latency_seconds": latency,
            }
            audit_logger.info(json.dumps(payload))
        except Exception:
            audit_logger.exception("audit_log_failed")
        return resp


def init_prometheus_metrics(app: Flask, metrics_path: str = "/metrics") -> None:
    @app.after_request
    def _metrics(resp: Response) -> Response:
        try:
            path = request.url_rule.rule if request.url_rule else request.path
            method = request.method
            status = str(resp.status_code)
            start = getattr(g, "_start_time", None)
            if start is not None:
                duration = time.perf_counter() - start
                REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
            REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        except Exception:
            logging.getLogger(__name__).exception("metrics_failed")
        return resp

    @app.get(metrics_path)
    def metrics() -> Response:
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)


def add_security_headers(app: Flask) -> None:
    @app.after_request
    def _headers(resp: Response) -> Response:
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "no-referrer")
        resp.headers.setdefault("Permissions-Policy", "geolocation=()")
        resp.headers.setdefault("Cache-Control", "no-store")
        return resp
