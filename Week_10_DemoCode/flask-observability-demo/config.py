import os


def env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value is not None else default


class Config:
    ENV = env("FLASK_ENV", "development")

    HOST = env("HOST", "0.0.0.0")
    PORT = int(env("PORT", "8000") or 8000)

    LOG_LEVEL = env("LOG_LEVEL", "INFO")
    LOG_FORMAT = env("LOG_FORMAT", "json")  # json|text

    PROMETHEUS_METRICS_PATH = env("METRICS_PATH", "/metrics")

    # OpenTelemetry
    OTEL_SERVICE_NAME = env("OTEL_SERVICE_NAME", "flask-observability-demo")
    OTEL_EXPORTER_OTLP_ENDPOINT = env("OTEL_EXPORTER_OTLP_ENDPOINT")  # e.g. http://localhost:4318
    OTEL_EXPORTER_OTLP_PROTOCOL = env("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")

    # Rate limiting
    RATE_LIMIT_DEFAULT = env("RATE_LIMIT_DEFAULT", "200 per minute")
    RATE_LIMIT_STORAGE_URI = env("RATE_LIMIT_STORAGE_URI", "memory://")  # production: redis://...

    # Circuit breaker
    CB_FAIL_MAX = int(env("CB_FAIL_MAX", "5") or 5)
    CB_RESET_TIMEOUT_SECONDS = int(env("CB_RESET_TIMEOUT_SECONDS", "30") or 30)

    # External dependency example
    EXTERNAL_URL = env("EXTERNAL_URL", "https://httpbin.org/status/200")
    EXTERNAL_TIMEOUT_SECONDS = float(env("EXTERNAL_TIMEOUT_SECONDS", "2.0") or 2.0)
