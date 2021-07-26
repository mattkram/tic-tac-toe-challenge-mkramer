from typing import Any
from typing import Dict
from typing import List

import marshmallow as ma
from flask import abort
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema

from tic_tac_toe.db import Game

api = Api()

blp = Blueprint(
    "tic-tac-toe",
    "tic-tac-toe",
    url_prefix="/api",
    description="API for Tic-Tac-Toe gameplay",
)


class CreateGameSchema(ma.Schema):
    """Schema used for handling POST request creating a new game."""

    players = ma.fields.List(ma.fields.String())


class AssignedPlayersSchema(ma.Schema):
    """Schema to represent which player is assigned to which position."""

    X = ma.fields.String()
    O = ma.fields.String()  # noqa: E741


class _GameSchemaBase(ma.Schema):
    """Common fields for Game serialization."""

    id = ma.fields.Int(dump_only=True)
    state = ma.fields.String()


class GameSchema(_GameSchemaBase):
    """The primary schema for data transfer between front- and back-end."""

    _player_name_map = ma.fields.Nested(
        AssignedPlayersSchema,
        data_key="player",
        dump_only=True,
    )


class UpdateGameSchema(_GameSchemaBase):
    """Specialized schema for game update, which ignores  extra fields passed in besides state."""

    class Meta:
        unknown = ma.EXCLUDE


@blp.route("/games")
class Games(MethodView):
    @blp.response(200, GameSchema(many=True))
    def get(self) -> List[Game]:
        """Return a list of games from the database."""
        return Game.query.all()

    @blp.arguments(CreateGameSchema())
    @blp.response(200, GameSchema)
    @blp.alt_response(422, ErrorSchema, description="More than two players specified")
    def post(self, data: Dict[str, List[str]]) -> Game:
        """Create a new game.

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


@blp.route("/games/<int:game_id>")
class GameByID(MethodView):
    @blp.response(200, GameSchema())
    def get(self, game_id: int) -> Game:
        """Return a specific game from the database."""
        game = Game.query.get(game_id)
        if game is None:
            return abort(404)
        return game

    @blp.arguments(UpdateGameSchema())
    @blp.response(200, GameSchema())
    @blp.alt_response(
        418, ErrorSchema, description="A teapot cannot process invalid moves"
    )
    def post(self, data: Dict[str, Any], *, game_id: int) -> Game:
        """Update the state of a game.

        Although the entire Game schema may be passed, the players and ID are considered
        immutable and only the game state will be updated.

        """
        game = Game.query.get(game_id)
        if game is None:
            return abort(404)

        try:
            game.state = data["state"]
        except ValueError as err:
            return abort(418, str(err))

        game.save()
        return game


def init_app(app: Flask) -> None:
    app.config.update(
        API_TITLE="Tic-Tac-Toe API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.2",
        OPENAPI_URL_PREFIX="/api/docs",
        OPENAPI_SWAGGER_UI_PATH="",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )
    api.init_app(app)
    api.register_blueprint(blp)
