import random
from typing import Any
from typing import Dict
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


def game_to_dict(game: Game) -> Dict[str, Any]:
    """Manually serialize a game, as a check against the Marshmallow schema."""
    return {
        "id": game.id,
        "state": game.state,
        "player": {X_CHAR: game.player_x.name, O_CHAR: game.player_o.name},
    }


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
    assert response.json == [game_to_dict(game) for game in games]


def test_post_new_game(client: FlaskClient) -> None:
    """When the games endpoint receives a POST request, save a new Game to the database
    and return it in the response."""
    response = client.post("/api/games", json={"players": ["Matt", "Bob"]})
    assert response.status_code == 200

    game, *additional_games = Game.query.all()
    assert not additional_games  # there should only be one game

    assert response.json == game_to_dict(game)

    # The names of the players in the response should be the same as from the JSON payload
    assert set(response.json["player"].values()) == {"Matt", "Bob"}


def test_post_new_game_bad_request(client: FlaskClient) -> None:
    """If too many names are provided, raise a 422 error."""
    response = client.post("/api/games", json={"players": ["Matt", "Bob", "Tim"]})
    assert response.status_code == 422


@pytest.fixture()
def game(games: List[Game]) -> Generator[Game, None, None]:
    """Create a single game."""
    game = Game()
    game.save()

    yield game

    game.delete()


def test_get_game_by_id(client: FlaskClient, game: Game) -> None:
    """Check the API return for retrieval of a game by ID."""
    response = client.get(f"/api/games/{game.id}")
    assert response.status_code == 200
    assert response.json == game_to_dict(game)


def test_get_nonexistant_game_by_id_raises_404(client: FlaskClient) -> None:
    """We get a 404 error if the game doesn't exist."""
    response = client.get("/api/games/1000")
    assert response.status_code == 404


def test_post_update_game_state(client: FlaskClient, game: Game) -> None:
    state = "X........"
    response = client.post(
        f"/api/games/{game.id}",
        json={
            "player": ["Whatever", "Doesn't", "Matter"],
            "state": state,
        },
    )
    assert response.status_code == 200
    assert response.json == game_to_dict(game)
    assert response.json["state"] == state
