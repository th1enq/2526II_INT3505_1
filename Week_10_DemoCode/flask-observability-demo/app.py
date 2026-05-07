import logging

from flask import Flask, jsonify

from config import Config
from extensions import create_breaker, create_http_session, init_limiter
from observability import (
    add_security_headers,
    init_audit_logging,
    init_prometheus_metrics,
    init_request_context,
    setup_logging,
)
from routes import create_api_blueprint
from tracing import setup_tracing


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    logger = logging.getLogger(__name__)

    setup_logging(app)
    init_request_context(app)
    init_audit_logging(app)
    add_security_headers(app)
    init_prometheus_metrics(app, metrics_path=app.config.get("PROMETHEUS_METRICS_PATH", "/metrics"))
    setup_tracing(app)

    limiter = init_limiter(app)
    breaker = create_breaker(app)
    http = create_http_session()

    app.register_blueprint(create_api_blueprint(app, limiter=limiter, breaker=breaker, http=http))

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
