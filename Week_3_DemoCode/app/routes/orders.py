from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .. import db
from ..schemas import OrderSchema, OrderQuerySchema, PaginatedOrdersSchema

blp = Blueprint(
    "orders", __name__,
    url_prefix="/api/v1",
    description="Operations on order resources",
)


@blp.route("/orders")
class OrderList(MethodView):

    @blp.arguments(OrderQuerySchema, location="query")
    @blp.response(200, PaginatedOrdersSchema)
    def get(self, args):
        """List all orders"""
        result = list(db.orders)
        if args["status"]:
            result = [o for o in result if o["status"] == args["status"]]
        if args["user_id"]:
            result = [o for o in result if o["user_id"] == args["user_id"]]
        if args["sort"]:
            result = sorted(result, key=lambda o: o[args["sort"]])
        page, limit = args["page"], args["limit"]
        paged = db.paginate(result, page, limit)
        return {"data": paged, "page": page, "limit": limit, "total": len(result)}

    @blp.arguments(OrderSchema)
    @blp.response(201, OrderSchema)
    def post(self, new_data):
        """Create a new order"""
        new_order = {"id": db.next_order_id, **new_data}
        db.orders.append(new_order)
        db.next_order_id += 1
        return new_order


@blp.route("/orders/<int:order_id>")
class Order(MethodView):

    @blp.response(200, OrderSchema)
    def get(self, order_id):
        """Get a single order by ID"""
        order = db.find(db.orders, order_id)
        if order is None:
            abort(404, message="Order not found")
        return order

    @blp.arguments(OrderSchema)
    @blp.response(200, OrderSchema)
    def put(self, new_data, order_id):
        """Replace an order entirely (full update)"""
        order = db.find(db.orders, order_id)
        if order is None:
            abort(404, message="Order not found")
        order.update(new_data)
        return order

    @blp.response(204)
    def delete(self, order_id):
        """Delete an order by ID"""
        order = db.find(db.orders, order_id)
        if order is None:
            abort(404, message="Order not found")
        db.orders[:] = [o for o in db.orders if o["id"] != order_id]
