import random
from collections import Counter
from typing import Any
from typing import Dict
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
    _state = db.Column("state", db.String(9))

    player_x_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    player_o_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)

    player_x = db.relationship("Player", foreign_keys=[player_x_id])
    player_o = db.relationship("Player", foreign_keys=[player_o_id])

    def __init__(self, *, players: List[str] = None):
        self.state = NULL_CHAR * 9
        self.player_names = players or []

    @property
    def state(self) -> str:
        """The board state. Validate on setting."""
        return self._state

    @state.setter
    def state(self, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError("state must be set to a string.")

        if self._state is not None:
            _validate_state(old=self._state, new=value)

        self._state = value

    @property
    def _player_name_map(self) -> Dict[str, str]:
        """Return a mapping of position to player name."""
        return {X_CHAR: self.player_x.name, O_CHAR: self.player_o.name}

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


def _validate_state(old: str, new: str) -> None:
    """Validate the board state update.

    Raises:
        ValueError: if not allowed.

    """
    changed = [o != n for o, n in zip(old, new)]
    if sum(changed) != 1:
        raise ValueError("More than one value has changed")

    for o, n in zip(old, new):
        if o != NULL_CHAR and o != n:
            raise ValueError("We have somehow undone an existing cell")

    old_counts = Counter(old)
    new_counts = Counter(new)

    if (old_counts[X_CHAR] + old_counts[O_CHAR]) % 2 == 1:
        if new_counts[X_CHAR] != old_counts[X_CHAR]:
            raise ValueError("It is O's turn!")
    else:
        if new_counts[O_CHAR] != old_counts[O_CHAR]:
            raise ValueError("It is X's turn!")


def init_app(app: Flask) -> None:
    """Initialize the database and ensure all tables are created."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
