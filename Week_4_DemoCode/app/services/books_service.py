from .. import db


def _normalize_payload(data: dict) -> dict:
    return {
        **data,
        "in_stock": data["stock"] > 0,
    }


def list_books(args: dict) -> dict:
    result = list(db.books)

    if args["author"]:
        keyword = args["author"].lower()
        result = [book for book in result if keyword in book["author"].lower()]

    if args["genre"]:
        keyword = args["genre"].lower()
        result = [book for book in result if keyword in book["genre"].lower()]

    if args["in_stock"] is not None:
        result = [book for book in result if book["in_stock"] == args["in_stock"]]

    if args["min_price"] is not None:
        result = [book for book in result if book["price"] >= args["min_price"]]

    if args["max_price"] is not None:
        result = [book for book in result if book["price"] <= args["max_price"]]

    if args["sort"]:
        result = sorted(result, key=lambda x: x[args["sort"]])

    page, limit = args["page"], args["limit"]
    paged = db.paginate(result, page, limit)
    return {
        "data": paged,
        "page": page,
        "limit": limit,
        "total": len(result),
    }


def create_book(data: dict) -> dict:
    new_book = {
        "id": db.next_book_id,
        **_normalize_payload(data),
    }
    db.books.append(new_book)
    db.next_book_id += 1
    return new_book


def update_book(book: dict, data: dict) -> dict:
    book.update(_normalize_payload(data))
    return book


def delete_book(book_id: int) -> None:
    db.books[:] = [x for x in db.books if x["id"] != book_id]
