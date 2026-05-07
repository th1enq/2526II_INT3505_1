import logging

import pybreaker
import requests
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from observability import (
    add_security_headers,
    init_audit_logging,
    init_prometheus_metrics,
    init_request_context,
    setup_logging,
)
from tracing import setup_tracing


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    setup_logging(app)
    init_request_context(app)
    init_audit_logging(app)
    add_security_headers(app)
    init_prometheus_metrics(app, metrics_path=app.config.get("PROMETHEUS_METRICS_PATH", "/metrics"))
    setup_tracing(app)

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get("RATE_LIMIT_DEFAULT", "200 per minute")],
        storage_uri=app.config.get("RATE_LIMIT_STORAGE_URI", "memory://"),
        headers_enabled=True,
    )
    limiter.init_app(app)

    breaker = pybreaker.CircuitBreaker(
        fail_max=app.config.get("CB_FAIL_MAX", 5),
        reset_timeout=app.config.get("CB_RESET_TIMEOUT_SECONDS", 30),
    )

    logger = logging.getLogger(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/v1/echo")
    @limiter.limit("30 per minute")
    def echo():
        msg = request.args.get("msg", "hello")
        logger.info("echo", extra={"echo_msg": msg})
        return jsonify({"msg": msg})

    @app.post("/v1/items")
    @limiter.limit("10 per minute")
    def create_item():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name is required"}), 400
        return jsonify({"id": "item_123", "name": name}), 201

    def _call_external() -> dict:
        url = app.config.get("EXTERNAL_URL")
        timeout = app.config.get("EXTERNAL_TIMEOUT_SECONDS", 2.0)
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return {"url": url, "status_code": r.status_code}

    @app.get("/v1/external")
    @limiter.limit("20 per minute")
    def external():
        try:
            result = breaker.call(_call_external)
            return jsonify({"ok": True, "result": result, "circuit": breaker.current_state}), 200
        except pybreaker.CircuitBreakerError:
            return jsonify({"ok": False, "error": "circuit_open", "circuit": breaker.current_state}), 503
        except Exception as e:
            logger.exception("external_call_failed")
            return jsonify({"ok": False, "error": str(e), "circuit": breaker.current_state}), 502

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "rate_limited", "detail": str(e)}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("internal_error")
        return jsonify({"error": "internal"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=(app.config.get("ENV") == "development"))
