import random
from typing import Generator
from typing import List

import pytest
from flask.testing import FlaskClient

from tic_tac_toe.db import Game
from tic_tac_toe.db import NULL_CHAR
from tic_tac_toe.db import O_CHAR
from tic_tac_toe.db import X_CHAR


@pytest.mark.parametrize(
    "url,expected_status_code",
    [
        ("/", 200),
        ("/non-existent", 404),
        ("/api/games", 200),
    ],
)
def test_response_status_code(
    client: FlaskClient, url: str, expected_status_code: int
) -> None:
    """Check the client response status code for different routes."""
    response = client.get(url)
    assert response.status_code == expected_status_code


def make_random_game() -> str:
    """Generate a random string consisting of O, X, and null characters."""
    return "".join(random.sample([O_CHAR, X_CHAR, NULL_CHAR], 1)[0] for _ in range(9))


@pytest.fixture()
def games() -> Generator[List[Game], None, None]:
    """Create several random games and store them in the database."""
    num_games = 5  # Number of games to generate, arbitrary
    games = []
    for _ in range(num_games):
        game = Game()
        game.state = make_random_game()
        game.save()
        games.append(game)

    yield games

    for game in games:
        game.delete()


def test_get_list_of_games(client: FlaskClient, games: List[Game]) -> None:
    """The JSON response should contain a list of serialized games."""
    response = client.get("/api/games")
    assert response.json == [{"id": game.id, "state": game.state} for game in games]
