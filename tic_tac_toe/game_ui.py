"""A basic UI for tic-tac-toe, using Dash.

Although not the most ideal use of a framework like Dash, the front-end will utilize the REST API
for data transfer instead of direct database interaction as would be more typical.

"""
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import Dash
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
        dbc.Button(id=f"cell-{row}-{col}"),
        width=4,
        className=" ".join(classes),
    )


board = [dbc.Row([make_cell(row, col) for col in range(3)]) for row in range(3)]

app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            dbc.Row(dbc.Col(board, width=dict(size=6, offset=3))),
            style={"margin-top": "30px"},
        ),
    ]
)


def init_app(server: Flask) -> None:
    app.init_app(server)
