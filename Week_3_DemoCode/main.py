from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}

swagger_template = {
    "info": {
        "title": "REST API Design Principles Demo",
        "description": (
            "A demo Flask API showcasing REST API design best practices:\n"
            "- Plural nouns, lowercase URLs, hyphens\n"
            "- Correct HTTP verbs (GET / POST / PUT / DELETE)\n"
            "- URL versioning (/api/v1/...)\n"
            "- Consistent error-response format\n"
            "- Pagination, filtering, and sorting via query parameters"
        ),
        "version": "1.0.0",
        "contact": {"email": "demo@example.com"},
    },
    "basePath": "/",
    "tags": [
        {"name": "Users", "description": "Operations on user resources"},
        {"name": "Orders", "description": "Operations on order resources"},
    ],
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id":     {"type": "integer", "example": 1},
                "name":   {"type": "string",  "example": "Alice"},
                "email":  {"type": "string",  "example": "alice@example.com"},
                "status": {"type": "string",  "example": "active",
                           "enum": ["active", "inactive"]},
            },
        },
        "Order": {
            "type": "object",
            "properties": {
                "id":      {"type": "integer", "example": 1},
                "user_id": {"type": "integer", "example": 1},
                "product": {"type": "string",  "example": "Laptop"},
                "status":  {"type": "string",  "example": "pending",
                            "enum": ["pending", "completed", "cancelled"]},
                "amount":  {"type": "number",  "example": 1200.00},
            },
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Resource not found"}
            },
        },
    },
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

_users = [
    {"id": 1, "name": "Alice",   "email": "alice@example.com",   "status": "active"},
    {"id": 2, "name": "Bob",     "email": "bob@example.com",     "status": "inactive"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "status": "active"},
]
_orders = [
    {"id": 1, "user_id": 1, "product": "Laptop",   "status": "completed", "amount": 1200.00},
    {"id": 2, "user_id": 1, "product": "Mouse",    "status": "pending",   "amount": 25.00},
    {"id": 3, "user_id": 2, "product": "Keyboard", "status": "pending",   "amount": 75.00},
]
_next_user_id  = 4
_next_order_id = 4


def _paginate(items: list, page: int, limit: int) -> list:
    start = (page - 1) * limit
    return items[start: start + limit]


def _error(message: str, code: int):
    # Consistent error-response format across all endpoints
    return jsonify({"error": message}), code


def _find(collection: list, item_id: int):
    return next((x for x in collection if x["id"] == item_id), None)


@app.route("/api/v1/users", methods=["GET"])
def list_users():
    """
    List all users
    ---
    tags:
      - Users
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: "Filter by status: active | inactive"
        enum: [active, inactive]
      - name: sort
        in: query
        type: string
        required: false
        description: "Sort by field: id | name | email"
        enum: [id, name, email]
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number (1-based)
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
        description: Items per page
    responses:
      200:
        description: Paginated list of users
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/definitions/User'
            page:
              type: integer
            limit:
              type: integer
            total:
              type: integer
    """
    global _users

    status = request.args.get("status")
    sort   = request.args.get("sort")
    page   = max(int(request.args.get("page",  1)), 1)
    limit  = min(max(int(request.args.get("limit", 10)), 1), 100)

    result = list(_users)

    # Filtering
    if status:
        result = [u for u in result if u["status"] == status]

    # Sorting
    if sort and sort in ("id", "name", "email"):
        result = sorted(result, key=lambda u: u[sort])

    total  = len(result)
    paged  = _paginate(result, page, limit)

    return jsonify({"data": paged, "page": page, "limit": limit, "total": total}), 200


@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get a single user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user ID
    responses:
      200:
        description: User found
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/Error'
    """
    user = _find(_users, user_id)
    if user is None:
        return _error("User not found", 404)
    return jsonify(user), 200


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
              example: Diana
            email:
              type: string
              example: diana@example.com
            status:
              type: string
              enum: [active, inactive]
              default: active
    responses:
      201:
        description: User created
        schema:
          $ref: '#/definitions/User'
      400:
        description: Invalid request body
        schema:
          $ref: '#/definitions/Error'
    """
    global _next_user_id
    data = request.get_json(silent=True)
    if not data:
        return _error("Request body must be JSON", 400)
    if not data.get("name") or not data.get("email"):
        return _error("Fields 'name' and 'email' are required", 400)

    new_user = {
        "id":     _next_user_id,
        "name":   data["name"],
        "email":  data["email"],
        "status": data.get("status", "active"),
    }
    _users.append(new_user)
    _next_user_id += 1
    return jsonify(new_user), 201


@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Replace a user entirely (full update)
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - status
          properties:
            name:
              type: string
              example: Alice Updated
            email:
              type: string
              example: alice_new@example.com
            status:
              type: string
              enum: [active, inactive]
    responses:
      200:
        description: User updated
        schema:
          $ref: '#/definitions/User'
      400:
        description: Invalid request body
        schema:
          $ref: '#/definitions/Error'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/Error'
    """
    user = _find(_users, user_id)
    if user is None:
        return _error("User not found", 404)

    data = request.get_json(silent=True)
    if not data:
        return _error("Request body must be JSON", 400)
    if not data.get("name") or not data.get("email") or not data.get("status"):
        return _error("Fields 'name', 'email', and 'status' are required for PUT", 400)

    user.update({
        "name":   data["name"],
        "email":  data["email"],
        "status": data["status"],
    })
    return jsonify(user), 200


@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user ID
    responses:
      204:
        description: User deleted (no content)
      404:
        description: User not found
        schema:
          $ref: '#/definitions/Error'
    """
    global _users
    user = _find(_users, user_id)
    if user is None:
        return _error("User not found", 404)
    _users = [u for u in _users if u["id"] != user_id]
    return "", 204


# ===========================================================================
# ORDERS  –  /api/v1/orders
# ===========================================================================

@app.route("/api/v1/orders", methods=["GET"])
def list_orders():
    """
    List all orders with optional filtering and pagination
    ---
    tags:
      - Orders
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: "Filter by status: pending | completed | cancelled"
        enum: [pending, completed, cancelled]
      - name: user_id
        in: query
        type: integer
        required: false
        description: Filter orders by user ID
      - name: sort
        in: query
        type: string
        required: false
        description: "Sort by field: id | amount | product"
        enum: [id, amount, product]
      - name: page
        in: query
        type: integer
        required: false
        default: 1
      - name: limit
        in: query
        type: integer
        required: false
        default: 10
    responses:
      200:
        description: Paginated list of orders
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/definitions/Order'
            page:
              type: integer
            limit:
              type: integer
            total:
              type: integer
    """
    global _orders

    status  = request.args.get("status")
    user_id = request.args.get("user_id", type=int)
    sort    = request.args.get("sort")
    page    = max(int(request.args.get("page",  1)), 1)
    limit   = min(max(int(request.args.get("limit", 10)), 1), 100)

    result = list(_orders)

    if status:
        result = [o for o in result if o["status"] == status]
    if user_id:
        result = [o for o in result if o["user_id"] == user_id]
    if sort and sort in ("id", "amount", "product"):
        result = sorted(result, key=lambda o: o[sort])

    total = len(result)
    paged = _paginate(result, page, limit)

    return jsonify({"data": paged, "page": page, "limit": limit, "total": total}), 200


@app.route("/api/v1/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    """
    Get a single order by ID
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID
    responses:
      200:
        description: Order found
        schema:
          $ref: '#/definitions/Order'
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/Error'
    """
    order = _find(_orders, order_id)
    if order is None:
        return _error("Order not found", 404)
    return jsonify(order), 200


@app.route("/api/v1/orders", methods=["POST"])
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - product
            - amount
          properties:
            user_id:
              type: integer
              example: 1
            product:
              type: string
              example: Monitor
            amount:
              type: number
              example: 350.00
            status:
              type: string
              enum: [pending, completed, cancelled]
              default: pending
    responses:
      201:
        description: Order created
        schema:
          $ref: '#/definitions/Order'
      400:
        description: Invalid request body
        schema:
          $ref: '#/definitions/Error'
    """
    global _next_order_id
    data = request.get_json(silent=True)
    if not data:
        return _error("Request body must be JSON", 400)
    if not data.get("user_id") or not data.get("product") or data.get("amount") is None:
        return _error("Fields 'user_id', 'product', and 'amount' are required", 400)

    new_order = {
        "id":      _next_order_id,
        "user_id": data["user_id"],
        "product": data["product"],
        "amount":  data["amount"],
        "status":  data.get("status", "pending"),
    }
    _orders.append(new_order)
    _next_order_id += 1
    return jsonify(new_order), 201


@app.route("/api/v1/orders/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    """
    Replace an order entirely (full update)
    ---
    tags:
      - Orders
    consumes:
      - application/json
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - product
            - amount
            - status
          properties:
            user_id:
              type: integer
              example: 1
            product:
              type: string
              example: Monitor Pro
            amount:
              type: number
              example: 400.00
            status:
              type: string
              enum: [pending, completed, cancelled]
    responses:
      200:
        description: Order updated
        schema:
          $ref: '#/definitions/Order'
      400:
        description: Invalid request body
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/Error'
    """
    order = _find(_orders, order_id)
    if order is None:
        return _error("Order not found", 404)

    data = request.get_json(silent=True)
    if not data:
        return _error("Request body must be JSON", 400)
    if not all(k in data for k in ("user_id", "product", "amount", "status")):
        return _error("Fields 'user_id', 'product', 'amount', and 'status' are required for PUT", 400)

    order.update({
        "user_id": data["user_id"],
        "product": data["product"],
        "amount":  data["amount"],
        "status":  data["status"],
    })
    return jsonify(order), 200


@app.route("/api/v1/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """
    Delete an order by ID
    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID
    responses:
      204:
        description: Order deleted (no content)
      404:
        description: Order not found
        schema:
          $ref: '#/definitions/Error'
    """
    global _orders
    order = _find(_orders, order_id)
    if order is None:
        return _error("Order not found", 404)
    _orders = [o for o in _orders if o["id"] != order_id]
    return "", 204

if __name__ == "__main__":
    print("Swagger UI available at: http://127.0.0.1:5000/docs/")
    app.run(debug=True, port=5000)
