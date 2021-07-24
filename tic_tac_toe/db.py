from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# String constants to represent player X, player O, and empty cell
X_CHAR = "X"
O_CHAR = "O"
NULL_CHAR = "."


class Game(db.Model):  # type: ignore
    """A database model to store a unique game and its state.

    The game state is represented by a nine-character string, where the first three characters
    represent the top row, the next three the middle row, and the final three the bottom row.

    """

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(9))

    def __init__(self) -> None:
        self.state = NULL_CHAR * 9

    def save(self) -> None:
        """Save the game to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """Delete the game from the database."""
        db.session.delete(self)
        db.session.commit()


def init_app(app: Flask) -> None:
    """Initialize the database and ensure all tables are created."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
