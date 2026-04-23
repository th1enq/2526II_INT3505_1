from datetime import datetime, timezone

from flask import Blueprint, Response, current_app, jsonify, make_response, request

from api_demo.services.deprecation import attach_deprecation_headers
from api_demo.services.openapi import generate_openapi_spec
from api_demo.services.users import users_payload
from api_demo.services.versioning import resolve_version

api_blueprint = Blueprint("api", __name__)

SWAGGER_UI_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Flask API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
    <style>
      html { box-sizing: border-box; overflow-y: scroll; }
      *, *:before, *:after { box-sizing: inherit; }
      body { margin: 0; background: #fafafa; }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js" crossorigin></script>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js" crossorigin></script>
    <script>
      window.onload = function () {
        window.ui = SwaggerUIBundle({
          url: '/openapi.json',
          dom_id: '#swagger-ui',
          deepLinking: true,
          presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
          layout: 'BaseLayout'
        });
      };
    </script>
  </body>
</html>
"""


@api_blueprint.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@api_blueprint.get("/api/v<int:version>/users")
def users_by_url_version(version: int):
    payload = users_payload(version)
    status_code = 200 if "error" not in payload else 400
    response = make_response(jsonify(payload), status_code)
    if version == 1 and status_code == 200:
        attach_deprecation_headers(response)
    return response


@api_blueprint.get("/api/users")
def users_by_header_or_query_version():
    version = resolve_version(request)
    payload = users_payload(version)
    status_code = 200 if "error" not in payload else 400
    response = make_response(jsonify(payload), status_code)
    if version == 1 and status_code == 200:
        attach_deprecation_headers(response)
    return response


@api_blueprint.post("/api/v1/payments")
def create_payment_v1():
    body = request.get_json(silent=True) or {}
    amount = body.get("amount")

    if amount is None:
        response = make_response(jsonify({"error": "amount is required"}), 400)
        return attach_deprecation_headers(response)

    response = make_response(
        jsonify(
            {
                "version": "v1",
                "payment_id": "pay_legacy_001",
                "amount": amount,
                "currency": body.get("currency", "USD"),
                "status": "created",
            }
        ),
        201,
    )
    return attach_deprecation_headers(response)


@api_blueprint.post("/api/v2/payments")
def create_payment_v2():
    body = request.get_json(silent=True) or {}
    amount = body.get("amount")
    currency = body.get("currency")
    customer_id = body.get("customer_id")

    missing = [field for field in ("amount", "currency", "customer_id") if body.get(field) is None]
    if missing:
        return jsonify({"error": "missing required fields", "fields": missing}), 400

    return (
        jsonify(
            {
                "version": "v2",
                "id": "pay_2026_001",
                "amount": amount,
                "currency": currency,
                "customer_id": customer_id,
                "status": "authorized",
                "links": {
                    "self": "/api/v2/payments/pay_2026_001",
                    "capture": "/api/v2/payments/pay_2026_001/capture",
                },
            }
        ),
        201,
    )


@api_blueprint.get("/openapi.json")
def openapi_spec():
    return jsonify(generate_openapi_spec(current_app))


@api_blueprint.get("/docs")
def swagger_ui():
    return Response(SWAGGER_UI_HTML, mimetype="text/html")
