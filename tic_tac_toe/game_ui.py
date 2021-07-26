"""A basic UI for tic-tac-toe, using Dash.

Although not the most ideal use of a framework like Dash, the front-end will utilize the REST API
for data transfer instead of direct database interaction as would be more typical.

"""
import re
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import requests
from dash import Dash
from dash.dependencies import Input
from dash.dependencies import MATCH
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from flask import Flask

API_URL = "http://localhost:5000/api"

app = Dash(
    __name__,
    title="Tic-Tac-Toe",
    assets_folder=(Path(__file__).parent / "assets").as_posix(),
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("play", href="/")),
        dbc.NavItem(dbc.NavLink("stats", href="/games")),
        dbc.NavItem(
            dbc.NavLink(
                "api docs", href="/api/docs", target="_blank", external_link=True
            )
        ),
    ],
    brand="Tic-Tac-Toe",
    color="secondary",
    brand_href="/",
    dark=True,
)


def make_cell(row: int, col: int, value: str = None) -> dbc.Col:
    """Create a cell, with appropriate borders"""
    classes = ["game-cell"]
    if row > 0:
        classes.append("border-top")
    if row < 2:
        classes.append("border-bottom")
    if col > 0:
        classes.append("border-left")
    if col < 2:
        classes.append("border-right")

    return dbc.Col(
        dbc.Button(value, id={"type": "cell", "index": f"{row},{col}"}),
        width=4,
        className=" ".join(classes),
    )


def make_board(state: str) -> List[dbc.Row]:
    """Create a list of lists containing the game cells."""
    rows = []
    for row in range(3):
        cells = []
        for col in range(3):
            value: Optional[str] = state[row * 3 + col]
            if value == ".":
                value = None
            cell = make_cell(row, col, value=value)
            cells.append(cell)
        rows.append(dbc.Row(cells))
    return rows


app.layout = html.Div(
    [
        navbar,
        dbc.Alert(id="winner-alert", color="success", is_open=False),
        dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            "New Game", id="new-game-button", style={"width": "100%"}
                        ),
                        width=dict(size=4, offset=4),
                        style={"margin-bottom": "20px"},
                    )
                ),
                dbc.Row(dbc.Col(id="board-container", width=dict(size=6, offset=3))),
            ],
            style={"margin-top": "30px"},
        ),
        dcc.Location(id="url"),
        html.Div(id="game-id", style={"display": "none"}),
    ]
)


@app.callback(
    Output("url", "pathname"),
    Input("new-game-button", "n_clicks"),
)
def create_new_game(n_clicks: Optional[int]) -> str:
    """When the "New Game" button is clicked, create a new game in the database and route to that
    game in the UI.
    """
    if n_clicks is None:
        raise PreventUpdate

    # Get a new game from the API
    response = requests.post(f"{API_URL}/games")
    # TODO: Should handle bad responses somehow
    game_data = response.json()
    return f"/game/{game_data['id']}"


def make_stats_table() -> Any:
    """Generate a table of game stats via a GET request to `/api/games`."""
    response = requests.get(f"{API_URL}/games")
    if response.status_code != 200:
        return "Error generating stats table"

    data = response.json()

    # Form a new data dictionary in the right format for the table, don't include incomplete games
    new_data = []
    for game_dict in data:
        state = game_dict["state"]
        winner = determine_winner([s if s != "." else None for s in state])
        if winner is not None:
            # Don't include incomplete games
            new_data.append(
                {
                    "id": game_dict["id"],
                    "player_x": game_dict["player"]["X"],
                    "player_o": game_dict["player"]["O"],
                    "state": state,
                    "winner": winner,
                    "url": f"[Link](/game/{game_dict['id']})",
                }
            )
    new_data.sort(key=lambda game: game["id"], reverse=True)

    return dash_table.DataTable(
        columns=[
            {"name": "ID", "id": "id"},
            {"name": "X", "id": "player_x"},
            {"name": "O", "id": "player_o"},
            {"name": "Board", "id": "state"},
            {"name": "Winner", "id": "winner"},
            {"name": "", "id": "url", "presentation": "markdown"},
        ],
        data=new_data,
    )


@app.callback(
    Output("board-container", "children"),
    Output("game-id", "children"),
    Input("url", "pathname"),
)
def display_game(url: str) -> Tuple[Any, Optional[str]]:
    """When the /game/<number> endpoint is hit, display the game board"""
    if url == "/games":
        return make_stats_table(), None

    m = re.match(r"/game/(\d+)", url)
    if m is None:
        # Don't display the board, "New Game" button only will be there
        return None, None

    # Try to get an existing game's state and fill the board with it if the game exists
    game_id = m.group(1)
    response = requests.get(f"{API_URL}/games/{game_id}")
    state = response.json().get("state", "." * 9)

    return make_board(state), game_id


def whose_move(cells: List[Optional[str]]) -> str:
    """Return X or O, depending on how many previous moves are on the board."""
    num_prev_moves = sum(v is not None for v in cells)
    if num_prev_moves % 2 == 0:
        return "X"
    else:
        return "O"


@app.callback(
    Output({"type": "cell", "index": MATCH}, "children"),
    Input({"type": "cell", "index": MATCH}, "n_clicks"),
    State({"type": "cell", "index": MATCH}, "children"),
    State({"type": "cell", "index": MATCH}, "id"),
    State("winner-alert", "children"),
    State("game-id", "children"),
    *[
        State({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
)
def handle_cell_click(
    n_clicks: Optional[int],
    old_state: Optional[str],
    cell_id: Dict[str, str],
    winner: Optional[str],
    game_id: Optional[str],
    *old_cells: Optional[str],
) -> str:
    """Set the value of a cell when it is clicked.

    The X or O value is derived by observing the current state of the board.

    """

    if winner is not None or old_state is not None or n_clicks is None:
        raise PreventUpdate

    # Extract the row and column from the "row,col" string in the index
    row, col = [int(val) for val in cell_id["index"].split(",")]

    # Decide whose move and replace the value in that cell
    cells = list(old_cells)  # make a copy and ensure a mutable list
    new_cell_value = whose_move(cells)
    cells[row * 3 + col] = new_cell_value

    # Convert cell value list to a string and update the game via the API
    state = [c if c is not None else "." for c in cells]
    state_str = "".join(state)
    response = requests.post(f"{API_URL}/games/{game_id}", json={"state": state_str})
    if response.status_code != 200:
        print(response.json())  # TODO: Don't let errors pass silently

    return new_cell_value


# A list of the indices of all routes that can win the game
# It is a list of lists, where the indices of the three cells in that route are stored
# Value cached here so it is only calculated once during import
_possible_winning_routes = []
for i in range(3):
    _possible_winning_routes.append([(i, j) for j in range(3)])
    _possible_winning_routes.append([(j, i) for j in range(3)])
_possible_winning_routes.append([(0, 0), (1, 1), (2, 2)])
_possible_winning_routes.append([(2, 0), (1, 1), (0, 2)])


def determine_winner(cell_values: Sequence[Optional[str]]) -> Optional[str]:
    """Determine whether there is winner, or if the game is a draw.

    Potential results are:
        * "X", "O": if either is the winner
        * "Draw": if game is a draw
        * None: if game is still ongoing

    """
    for route in _possible_winning_routes:
        route_values = set()  # unique values in this route
        for r, c in route:
            route_values.add(cell_values[r * 3 + c])

        if len(route_values) == 1:
            # If only one unique value is not None, that is the winner
            (winner,) = route_values
            if winner is not None:
                return winner

    if all(v is not None for v in cell_values):
        return "Draw"

    return None


@app.callback(
    Output("winner-alert", "children"),
    Output("winner-alert", "color"),
    Output("winner-alert", "is_open"),
    Input("url", "pathname"),
    *[
        Input({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
)
def identify_winner(url: str, *cell_values: Optional[str]) -> Tuple[str, str, bool]:
    """Observe all cell values and identify if any player has won.

    Trigger on page load to capture finished games."""
    if not url.startswith("/game"):
        # Only display alert on game page
        return "", "", False

    winner = determine_winner(cell_values)
    if winner == "Draw":
        return "Draw", "warning", True
    elif winner is not None:
        return f"{winner} has won!", "success", True

    raise PreventUpdate


def init_app(server: Flask) -> None:
    app.init_app(server)
