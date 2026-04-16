from flask import Flask

from .routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["ITEMS"] = []
    app.config["NEXT_ITEM_ID"] = 1
    app.register_blueprint(api_bp)
    return app
