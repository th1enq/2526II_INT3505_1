books = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "published_year": 2008,
        "genre": "Software Engineering",
        "price": 39.99,
        "stock": 10,
        "in_stock": True,
    },
    {
        "id": 2,
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "isbn": "9781449373320",
        "published_year": 2017,
        "genre": "Data Systems",
        "price": 49.99,
        "stock": 5,
        "in_stock": True,
    },
    {
        "id": 3,
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "isbn": "9780135957059",
        "published_year": 2019,
        "genre": "Software Engineering",
        "price": 44.99,
        "stock": 0,
        "in_stock": False,
    },
]
next_book_id = 4


def paginate(items: list, page: int, limit: int) -> list:
    start = (page - 1) * limit
    return items[start : start + limit]


def find_by_id(collection: list, item_id: int):
    return next((x for x in collection if x["id"] == item_id), None)
