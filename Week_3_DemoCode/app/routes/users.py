from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .. import db
from ..schemas import UserSchema, UserQuerySchema, PaginatedUsersSchema

blp = Blueprint(
    "users", __name__,
    url_prefix="/api/v1",
    description="Operations on user resources",
)


@blp.route("/users")
class UserList(MethodView):

    @blp.arguments(UserQuerySchema, location="query")
    @blp.response(200, PaginatedUsersSchema)
    def get(self, args):
        """List all users"""
        result = list(db.users)
        if args["status"]:
            result = [u for u in result if u["status"] == args["status"]]
        if args["sort"]:
            result = sorted(result, key=lambda u: u[args["sort"]])
        page, limit = args["page"], args["limit"]
        paged = db.paginate(result, page, limit)
        return {"data": paged, "page": page, "limit": limit, "total": len(result)}

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, new_data):
        """Create a new user"""
        new_user = {"id": db.next_user_id, **new_data}
        db.users.append(new_user)
        db.next_user_id += 1
        return new_user


@blp.route("/users/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get a single user by ID"""
        user = db.find(db.users, user_id)
        if user is None:
            abort(404, message="User not found")
        return user

    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self, new_data, user_id):
        """Replace a user entirely (full update)"""
        user = db.find(db.users, user_id)
        if user is None:
            abort(404, message="User not found")
        user.update(new_data)
        return user

    @blp.response(204)
    def delete(self, user_id):
        """Delete a user by ID"""
        user = db.find(db.users, user_id)
        if user is None:
            abort(404, message="User not found")
        db.users[:] = [u for u in db.users if u["id"] != user_id]
