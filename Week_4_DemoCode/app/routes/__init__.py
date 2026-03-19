from .books import blp as books_blp


def register_routes(api):
    api.register_blueprint(books_blp)
