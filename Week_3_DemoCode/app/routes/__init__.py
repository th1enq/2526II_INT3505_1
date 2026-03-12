from .users import blp as users_blp
from .orders import blp as orders_blp


def register_routes(api):
    api.register_blueprint(users_blp)
    api.register_blueprint(orders_blp)
