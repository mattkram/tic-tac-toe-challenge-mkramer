from typing import Generator

import pytest

from tic_tac_toe.db import Game
from tic_tac_toe.db import NULL_CHAR


@pytest.fixture()
def game() -> Generator[Game, None, None]:
    """Create a new game in the database."""
    game = Game()
    game.save()
    yield Game.query.one()  # new instance
    game.delete()


def test_save_game(game: Game) -> None:
    """The game has been saved to the database and retrieved."""
    assert game.id == 1
    assert game.state == NULL_CHAR * 9


def test_delete_game(game: Game) -> None:
    """After we delete the game, there are no games in the database."""
    game.delete()
    assert Game.query.get(game.id) is None
