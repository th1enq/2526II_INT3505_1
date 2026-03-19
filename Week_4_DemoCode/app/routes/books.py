from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .. import db
from ..schemas import BookQuerySchema, BookSchema, PaginatedBooksSchema

blp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/v1",
    description="Operations on book resources",
)


@blp.route("/books")
class BookList(MethodView):

    @blp.arguments(BookQuerySchema, location="query")
    @blp.response(200, PaginatedBooksSchema)
    def get(self, args):
        """List books with filters, sorting, and pagination"""
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
        return {"data": paged, "page": page, "limit": limit, "total": len(result)}

    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, new_data):
        """Create a new book"""
        new_book = {
            "id": db.next_book_id,
            **new_data,
            "in_stock": new_data["stock"] > 0,
        }
        db.books.append(new_book)
        db.next_book_id += 1
        return new_book


@blp.route("/books/<int:book_id>")
class Book(MethodView):

    @blp.response(200, BookSchema)
    def get(self, book_id):
        """Get book by ID.

        Returns detailed information for a single book.
        """
        book = db.find_by_id(db.books, book_id)
        if book is None:
            abort(404, message="Book not found")
        return book

    @blp.arguments(BookSchema)
    @blp.response(200, BookSchema)
    def put(self, new_data, book_id):
        """Replace a book"""
        book = db.find_by_id(db.books, book_id)
        if book is None:
            abort(404, message="Book not found")

        new_payload = {
            **new_data,
            "in_stock": new_data["stock"] > 0,
        }
        book.update(new_payload)
        return book

    @blp.response(204)
    def delete(self, book_id):
        """Delete a book by ID"""
        book = db.find_by_id(db.books, book_id)
        if book is None:
            abort(404, message="Book not found")
        db.books[:] = [x for x in db.books if x["id"] != book_id]
