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


def test_app_info(client):
    response = client.get("/api/info")

    assert response.status_code == 200
    assert response.get_json() == {"name": "flask-demo", "version": "1.0.0"}


def test_sum_numbers_success(client):
    response = client.post("/api/math/sum", json={"numbers": [1, 2.5, 3]})

    assert response.status_code == 200
    assert response.get_json() == {"count": 3, "sum": 6.5}


def test_sum_numbers_invalid_payload(client):
    response = client.post("/api/math/sum", json={"numbers": []})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Field 'numbers' must be a non-empty list"
    }


def test_sum_numbers_non_numeric_element(client):
    response = client.post("/api/math/sum", json={"numbers": [1, "2", 3]})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "All elements in 'numbers' must be numeric"
    }


def test_items_initially_empty(client):
    response = client.get("/api/items")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item_success(client):
    response = client.post("/api/items", json={"name": "  notebook  "})

    assert response.status_code == 201
    body = response.get_json()
    assert body["id"] == 1
    assert body["name"] == "notebook"
    assert "created_at" in body


def test_create_item_missing_name(client):
    response = client.post("/api/items", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Field 'name' is required"}


def test_get_item_by_id_success(client):
    created = client.post("/api/items", json={"name": "book"}).get_json()

    response = client.get(f"/api/items/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "book"


def test_get_item_not_found(client):
    response = client.get("/api/items/99")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Item not found"}


def test_delete_item_success(client):
    created = client.post("/api/items", json={"name": "eraser"}).get_json()

    delete_response = client.delete(f"/api/items/{created['id']}")
    assert delete_response.status_code == 204

    list_response = client.get("/api/items")
    assert list_response.status_code == 200
    assert list_response.get_json() == []


def test_delete_item_not_found(client):
    response = client.delete("/api/items/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Item not found"}
