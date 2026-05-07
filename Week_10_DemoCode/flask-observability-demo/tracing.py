from __future__ import annotations

import logging

from flask import Flask


def setup_tracing(app: Flask) -> None:
    """OpenTelemetry instrumentation.

    - If OTEL_EXPORTER_OTLP_ENDPOINT is set: exports OTLP (http/protobuf by default)
    - Else: uses ConsoleSpanExporter (prints spans to stdout)
    """

    logger = logging.getLogger(__name__)

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
            SimpleSpanProcessor,
        )
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
    except Exception as e:
        logger.warning("tracing_disabled", extra={"reason": str(e)})
        return

    service_name = app.config.get("OTEL_SERVICE_NAME", "flask-observability-demo")
    endpoint = app.config.get("OTEL_EXPORTER_OTLP_ENDPOINT")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
