from flask import Flask


def create_app() -> Flask:
    """Initialize the application object."""

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return "Hello"

    return app
