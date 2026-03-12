users = [
    {"id": 1, "name": "Alice",   "email": "alice@example.com",   "status": "active"},
    {"id": 2, "name": "Bob",     "email": "bob@example.com",     "status": "inactive"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "status": "active"},
]
orders = [
    {"id": 1, "user_id": 1, "product": "Laptop",   "status": "completed", "amount": 1200.00},
    {"id": 2, "user_id": 1, "product": "Mouse",    "status": "pending",   "amount": 25.00},
    {"id": 3, "user_id": 2, "product": "Keyboard", "status": "pending",   "amount": 75.00},
]
next_user_id  = 4
next_order_id = 4


def paginate(items: list, page: int, limit: int) -> list:
    start = (page - 1) * limit
    return items[start: start + limit]


def find(collection: list, item_id: int):
    return next((x for x in collection if x["id"] == item_id), None)
