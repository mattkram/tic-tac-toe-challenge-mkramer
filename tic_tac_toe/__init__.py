from pathlib import Path
from typing import Any
from typing import Dict

from flask import Flask

INSTANCE_DIR = Path(__file__).parents[1] / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


def create_app(config: Dict[str, Any] = None) -> Flask:
    """Initialize the application object."""

    app = Flask(__name__)

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"sqlite:///{INSTANCE_DIR / 'tic-tac-toe.db'}"
    if config is not None:
        app.config.from_mapping(config)

    @app.route("/")
    def index() -> str:
        return "Hello"

    from . import db

    db.init_app(app)

    return app
