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

app.layout = html.Div("Hello")


def init_app(server: Flask) -> None:
    app.init_app(server)
