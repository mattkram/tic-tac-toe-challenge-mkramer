from typing import List

import marshmallow as ma
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api
from flask_smorest import Blueprint

from tic_tac_toe.db import Game

api = Api()

blp = Blueprint(
    "tic-tac-toe",
    "tic-tac-toe",
    url_prefix="/api",
    description="API for Tic-Tac-Toe gameplay",
)


class GameSchema(ma.Schema):
    id = ma.fields.Int(dump_only=True)
    state = ma.fields.String()


@blp.route("/games")
class Games(MethodView):
    @blp.response(200, GameSchema(many=True))
    def get(self) -> List[Game]:
        """Return a list of Games from the database as a JSON document."""
        return Game.query.all()


def init_app(app: Flask) -> None:
    app.config["API_TITLE"] = "Tic-Tac-Toe API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    api.init_app(app)
    api.register_blueprint(blp)
