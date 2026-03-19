from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .. import db
from ..schemas import BookQuerySchema, BookSchema, PaginatedBooksSchema
from ..services import create_book, delete_book, list_books, update_book

blp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/v1",
    description="Operations on book resources",
)


def _find_or_404(book_id):
    book = db.find_by_id(db.books, book_id)
    if book is None:
        abort(404, message="Book not found")
    return book


@blp.route("/books")
class BookList(MethodView):

    @blp.arguments(BookQuerySchema, location="query")
    @blp.response(200, PaginatedBooksSchema)
    def get(self, args):
        """List books with filters, sorting, and pagination"""
        return list_books(args)

    @blp.arguments(BookSchema)
    @blp.response(201, BookSchema)
    def post(self, new_data):
        """Create a new book"""
        return create_book(new_data)


@blp.route("/books/<int:book_id>")
class Book(MethodView):

    @blp.response(200, BookSchema)
    def get(self, book_id):
        """Get book by ID.

        Returns detailed information for a single book.
        """
        return _find_or_404(book_id)

    @blp.arguments(BookSchema)
    @blp.response(200, BookSchema)
    def put(self, new_data, book_id):
        """Replace a book"""
        book = _find_or_404(book_id)
        return update_book(book, new_data)

    @blp.response(204)
    def delete(self, book_id):
        """Delete a book by ID"""
        _find_or_404(book_id)
        delete_book(book_id)
