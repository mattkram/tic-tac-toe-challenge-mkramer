from typing import Generator
from typing import List

import pytest

from tic_tac_toe.db import Game
from tic_tac_toe.db import NULL_CHAR
from tic_tac_toe.db import Player


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
    assert game.player_x is not None
    assert game.player_o is not None


@pytest.fixture()
def games() -> Generator[List[Game], None, None]:
    """Create multiple games with the same two players, randomly assigned to "X" and "O"."""
    games = []
    for _ in range(10):
        game = Game(players=["Matt", "Bob"])
        game.save()
        games.append(game)
    yield games
    for game in games:
        game.delete()


def test_assign_players_randomly(games: List[Game]) -> None:
    """Given enough games, both players should be assigned to "X" at least once."""
    player_x_names = {game.player_x.name for game in games}
    assert len(player_x_names) == 2
    assert Player.query.count() == 2


def test_delete_game(game: Game) -> None:
    """After we delete the game, there are no games in the database."""
    game.delete()
    assert Game.query.get(game.id) is None
