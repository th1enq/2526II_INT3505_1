import pybreaker
import requests
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def init_limiter(app: Flask) -> Limiter:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get("RATE_LIMIT_DEFAULT", "200 per minute")],
        storage_uri=app.config.get("RATE_LIMIT_STORAGE_URI", "memory://"),
        headers_enabled=True,
    )
    limiter.init_app(app)
    return limiter


def create_breaker(app: Flask) -> pybreaker.CircuitBreaker:
    return pybreaker.CircuitBreaker(
        fail_max=app.config.get("CB_FAIL_MAX", 5),
        reset_timeout=app.config.get("CB_RESET_TIMEOUT_SECONDS", 30),
    )


def create_http_session() -> requests.Session:
    return requests.Session()
