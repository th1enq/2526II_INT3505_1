import logging

import pybreaker
import requests
from flask import Blueprint, Flask, jsonify, request
from flask_limiter import Limiter


def create_api_blueprint(
    app: Flask,
    limiter: Limiter,
    breaker: pybreaker.CircuitBreaker,
    http: requests.Session,
) -> Blueprint:
    logger = logging.getLogger(__name__)
    bp = Blueprint("api", __name__)

    @bp.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @bp.get("/v1/echo")
    @limiter.limit("30 per minute")
    def echo():
        msg = request.args.get("msg", "hello")
        logger.info("echo msg=%s", msg)
        return jsonify({"msg": msg})

    @bp.post("/v1/items")
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
        r = http.get(url, timeout=timeout)
        r.raise_for_status()
        return {"url": url, "status_code": r.status_code}

    @bp.get("/v1/external")
    @limiter.limit("20 per minute")
    def external():
        try:
            result = breaker.call(_call_external)
            return (
                jsonify(
                    {
                        "ok": True,
                        "result": result,
                        "circuit": str(breaker.current_state),
                    }
                ),
                200,
            )
        except pybreaker.CircuitBreakerError:
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "circuit_open",
                        "circuit": str(breaker.current_state),
                    }
                ),
                503,
            )
        except Exception as e:
            logger.exception("external_call_failed")
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": str(e),
                        "circuit": str(breaker.current_state),
                    }
                ),
                502,
            )

    return bp
