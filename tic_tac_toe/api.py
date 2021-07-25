from typing import Dict
from typing import List

import marshmallow as ma
from flask import abort
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


class GameCreateSchema(ma.Schema):
    """Schema used for handling POST request creating a new game."""

    players = ma.fields.List(ma.fields.String())


class GameSchema(ma.Schema):
    """The primary schema for data transfer between front- and back-end."""

    id = ma.fields.Int(dump_only=True)
    state = ma.fields.String()
    player = ma.fields.Method("get_player_name_map")

    def get_player_name_map(self, game: Game) -> Dict[str, str]:
        """Return a mapping of the assigned symbol to the player name."""
        return {"X": game.player_x.name, "O": game.player_o.name}


@blp.route("/games")
class Games(MethodView):
    @blp.response(200, GameSchema(many=True))
    def get(self) -> List[Game]:
        """Return a list of Games from the database as a JSON document."""
        return Game.query.all()

    @blp.arguments(GameCreateSchema())
    @blp.response(200, GameSchema)
    def post(self, data: Dict[str, List[str]]) -> Game:
        """On POST request, create a new game.

        The POST request can receive an optional payload dictionary with form
        {"players": ["Player 1", "Player 2"]} to associate the game with known players.

        Otherwise, if no payload is provided, random player names will be created and used.

        """
        player_names = data.get("players")
        game = Game(players=player_names)
        try:
            game.save()
        except ValueError as err:
            abort(422, str(err))
        return game


def init_app(app: Flask) -> None:
    app.config["API_TITLE"] = "Tic-Tac-Toe API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    api.init_app(app)
    api.register_blueprint(blp)
