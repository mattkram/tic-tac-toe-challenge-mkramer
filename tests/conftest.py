from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tic_tac_toe import create_app


@pytest.fixture()
def app() -> Flask:
    return create_app()


@pytest.fixture()
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    with app.test_client() as client:
        yield client
