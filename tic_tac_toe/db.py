import random
from typing import Any
from typing import List

from flask import Flask
from flask_sqlalchemy import Model
from flask_sqlalchemy import SQLAlchemy

# String constants to represent player X, player O, and empty cell
X_CHAR = "X"
O_CHAR = "O"
NULL_CHAR = "."


class _BaseModel(Model):
    """A base model, implementing simple shorthand methods for saving and deleting records."""

    def save(self) -> None:
        """Save the game to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """Delete the game from the database."""
        db.session.delete(self)
        db.session.commit()


db = SQLAlchemy(model_class=_BaseModel)


class Player(db.Model):  # type: ignore
    """A database model representing a player, assumed to have a unique name."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)

    @classmethod
    def get_or_create(cls, **kwargs: Any) -> "Player":
        """Get an object from database by performing a `filter_by(**kwargs)` query. If no result,
        create a new object."""
        obj = cls.query.filter_by(**kwargs).one_or_none()
        if obj is not None:
            return obj
        return cls(**kwargs)


class Game(db.Model):  # type: ignore
    """A database model to store a unique game and its state.

    The game state is represented by a nine-character string, where the first three characters
    represent the top row, the next three the middle row, and the final three the bottom row.

    """

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(9))

    player_x_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player_o_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)

    player_x = db.relationship("Player", foreign_keys=[player_x_id])
    player_o = db.relationship("Player", foreign_keys=[player_o_id])

    def __init__(self, *, players: List[str] = None):
        self.state = NULL_CHAR * 9
        self.player_names = players or []

    def _assign_players(self) -> None:
        """Assign players to the game, randomly choosing which is "X" an which "O".

        Raises:
            ValueError: If more than two names are provided.

        """
        num_players = len(self.player_names)
        if num_players > 2:
            raise ValueError(
                f"Only two players can be specified, you provided {num_players}"
            )

        # Create any missing player names
        for i in range(2 - num_players):
            self.player_names.append(f"Player {Player.query.count() + i}")

        players = [Player.get_or_create(name=name) for name in self.player_names]
        random.shuffle(players)
        self.player_o, self.player_x = players

    def save(self) -> None:
        """Use specified player names to create foreign keys if needed."""
        if self.player_x_id is None:
            self._assign_players()
        super().save()


def init_app(app: Flask) -> None:
    """Initialize the database and ensure all tables are created."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
