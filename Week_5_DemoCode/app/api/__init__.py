from flask import Flask

from app.api.books import books_bp
from app.api.health import health_bp
from app.api.users import users_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(books_bp)
