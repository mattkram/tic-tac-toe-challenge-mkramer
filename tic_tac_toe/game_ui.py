"""A basic UI for tic-tac-toe, using Dash.

Although not the most ideal use of a framework like Dash, the front-end will utilize the REST API
for data transfer instead of direct database interaction as would be more typical.

"""
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import Dash
from dash.dependencies import Input
from dash.dependencies import MATCH
from dash.dependencies import Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from flask import Flask

# A list of the indices of all routes that can win the game
WINNING_ROUTES = []
for i in range(3):
    WINNING_ROUTES.append([(i, j) for j in range(3)])
    WINNING_ROUTES.append([(j, i) for j in range(3)])
WINNING_ROUTES.append([(0, 0), (1, 1), (2, 2)])
WINNING_ROUTES.append([(2, 0), (1, 1), (0, 2)])


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
        html.Div(id="winner"),
    ]
)


@app.callback(
    Output({"type": "cell", "index": MATCH}, "children"),
    Input({"type": "cell", "index": MATCH}, "n_clicks"),
    State({"type": "cell", "index": MATCH}, "children"),
    *[
        State({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
    State("winner", "children"),
)
def handle_cell_click(
    n_clicks: Optional[int], old_state: Optional[str], *args: Any
) -> str:
    """Set the value of a cell when it is clicked.

    The X or O value is derived by observing the current state of the board.

    """
    *old_cells, winner = args

    if winner is not None or old_state is not None or n_clicks is None:
        raise PreventUpdate

    num_prev_moves = sum(v is not None for v in old_cells)
    if num_prev_moves % 2 == 0:
        return "X"
    else:
        return "O"


@app.callback(
    Output("winner", "children"),
    *[
        Input({"type": "cell", "index": f"{row},{col}"}, "children")
        for row in range(3)
        for col in range(3)
    ],
)
def identify_winner(*cell_values: Optional[str]) -> Optional[str]:
    """Observe all cell values and identify if any player has won."""
    for route in WINNING_ROUTES:
        route_values = set()
        for r, c in route:
            route_values.add(cell_values[r * 3 + c])

        if len(route_values) == 1:
            winner = route_values.pop()
            if winner is not None:
                return f"{winner} has won!"
    return None


def init_app(server: Flask) -> None:
    app.init_app(server)
