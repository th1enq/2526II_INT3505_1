from app import app


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_url_version_v1_has_deprecation_headers():
    c = client()
    response = c.get("/api/v1/users")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["version"] == "v1"
    assert "name" in payload["users"][0]
    assert response.headers.get("Deprecation") == "true"
    assert response.headers.get("Sunset")


def test_url_version_v2_schema_changed():
    c = client()
    response = c.get("/api/v2/users")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["version"] == "v2"
    assert "full_name" in payload["users"][0]
    assert "name" not in payload["users"][0]


def test_query_param_version_strategy():
    c = client()
    response = c.get("/api/users?version=2")

    assert response.status_code == 200
    assert response.get_json()["version"] == "v2"


def test_header_version_strategy_x_api_version():
    c = client()
    response = c.get("/api/users", headers={"X-API-Version": "v2"})

    assert response.status_code == 200
    assert response.get_json()["version"] == "v2"


def test_header_version_strategy_accept_media_type():
    c = client()
    response = c.get("/api/users", headers={"Accept": "application/vnd.demo.v2+json"})

    assert response.status_code == 200
    assert response.get_json()["version"] == "v2"


def test_default_version_is_v1_when_not_specified():
    c = client()
    response = c.get("/api/users")

    assert response.status_code == 200
    assert response.get_json()["version"] == "v1"


def test_payment_v2_requires_new_fields():
    c = client()
    response = c.post("/api/v2/payments", json={"amount": 100})

    assert response.status_code == 400
    payload = response.get_json()
    assert "currency" in payload["fields"]
    assert "customer_id" in payload["fields"]


def test_payment_v1_deprecated_but_still_works():
    c = client()
    response = c.post("/api/v1/payments", json={"amount": 100, "currency": "USD"})

    assert response.status_code == 201
    assert response.get_json()["version"] == "v1"
    assert response.headers.get("Deprecation") == "true"


def test_openapi_is_generated_from_code():
    c = client()
    response = c.get("/openapi.json")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["openapi"] == "3.0.3"
    assert "/api/v{version}/users" in payload["paths"]
    assert "/api/v2/payments" in payload["paths"]


def test_swagger_ui_docs_page_available():
    c = client()
    response = c.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    body = response.get_data(as_text=True)
    assert "SwaggerUIBundle" in body
    assert "/openapi.json" in body
