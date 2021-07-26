"""A basic UI for tic-tac-toe, using Dash.

Although not the most ideal use of a framework like Dash, the front-end will utilize the REST API
for data transfer instead of direct database interaction as would be more typical.

"""
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input
from dash.dependencies import MATCH
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from flask import Flask

app = Dash(
    __name__,
    title="Tic-Tac-Toe",
    assets_folder=(Path(__file__).parent / "assets").as_posix(),
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("game", href="/")),
        dbc.NavItem(
            dbc.NavLink(
                "api docs", href="/api/docs", target="_blank", external_link=True
            )
        ),
    ],
    brand="Tic-Tac-Toe",
    color="secondary",
    dark=True,
)


def make_cell(row: int, col: int) -> dbc.Col:
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
        dbc.Button(id={"type": "cell", "index": f"{row},{col}"}),
        width=4,
        className=" ".join(classes),
    )


def make_board() -> List[dbc.Row]:
    """Create a list of lists containing the game cells."""
    return [dbc.Row([make_cell(row, col) for col in range(3)]) for row in range(3)]


app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            dbc.Row(dbc.Col(make_board(), width=dict(size=6, offset=3))),
            style={"margin-top": "30px"},
        ),
        dbc.Alert(id="winner-alert", color="success", is_open=False),
    ]
)


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
    *[
        State({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
    State("winner-alert", "children"),
)
def handle_cell_click(
    n_clicks: Optional[int],
    old_state: Optional[str],
    cell_id: Dict[str, str],
    *args: Any,
) -> str:
    """Set the value of a cell when it is clicked.

    The X or O value is derived by observing the current state of the board.

    """
    *old_cells, winner = args

    if winner is not None or old_state is not None or n_clicks is None:
        raise PreventUpdate

    # Extract the row and column from the "row,col" string in the index
    row, col = [int(val) for val in cell_id["index"].split(",")]

    # Decide whose move and replace the value in that cell
    new_cell_value = whose_move(old_cells)
    old_cells[row * 3 + col] = new_cell_value

    # Convert cell value list to a string for the API
    vals = [c if c is not None else "." for c in old_cells]
    print("".join(vals))

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


@app.callback(
    Output("winner-alert", "children"),
    Output("winner-alert", "color"),
    Output("winner-alert", "is_open"),
    *[
        Input({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
)
def identify_winner(*cell_values: Optional[str]) -> Tuple[str, str, bool]:
    """Observe all cell values and identify if any player has won."""
    for route in _possible_winning_routes:
        route_values = set()  # unique values in this route
        for r, c in route:
            route_values.add(cell_values[r * 3 + c])

        if len(route_values) == 1:
            # If only one unique value is not None, that is the winner
            (winner,) = route_values
            if winner is not None:
                return f"{winner} has won!", "success", True

    if all(v is not None for v in cell_values):
        return "Draw", "warning", True

    raise PreventUpdate


def init_app(server: Flask) -> None:
    app.init_app(server)
