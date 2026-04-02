from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields

from core.auth.decorators import role_required, scope_required


def create_protected_namespace(book_service):
    api_ns = Namespace("api", description="Protected business endpoints")

    book_model = api_ns.model(
        "Book",
        {
            "id": fields.Integer,
            "title": fields.String,
            "author": fields.String,
        },
    )

    book_create_request = api_ns.model(
        "BookCreateRequest",
        {
            "title": fields.String(required=True),
            "author": fields.String(required=True),
        },
    )

    @api_ns.route("/me")
    class MeResource(Resource):
        @api_ns.doc(security="BearerAuth")
        @jwt_required()
        @scope_required("profile:read")
        def get(self):
            return {
                "username": get_jwt_identity(),
                "roles": get_jwt().get("roles", []),
                "scopes": get_jwt().get("scopes", []),
            }, 200

    @api_ns.route("/admin/reports")
    class AdminReportsResource(Resource):
        @api_ns.doc(security="BearerAuth")
        @jwt_required()
        @role_required("admin")
        @scope_required("admin:read")
        def get(self):
            return {
                "message": "Sensitive admin report data",
                "requested_by": get_jwt_identity(),
            }, 200

    @api_ns.route("/books")
    class BooksResource(Resource):
        @api_ns.doc(security="BearerAuth")
        @api_ns.marshal_list_with(book_model)
        @jwt_required()
        @scope_required("books:read")
        def get(self):
            return book_service.list_books(), 200

        @api_ns.doc(security="BearerAuth")
        @api_ns.expect(book_create_request, validate=True)
        @jwt_required()
        @scope_required("books:write")
        @role_required("librarian", "admin")
        def post(self):
            payload = api_ns.payload
            return book_service.create_book(payload["title"], payload["author"]), 201

    return api_ns
