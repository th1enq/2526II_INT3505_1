def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "flask-demo"}


def test_echo_message_success(client):
    response = client.post("/api/echo", json={"message": "hello"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["message"] == "hello"
    assert "received_at" in body


def test_echo_message_missing_field(client):
    response = client.post("/api/echo", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'message' is required"}
