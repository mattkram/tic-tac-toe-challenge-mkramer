from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from tic_tac_toe import create_app


@pytest.fixture(autouse=True)
def app() -> Generator[Flask, None, None]:
    """Create a new application with a temporary database."""
    app = create_app({"SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        yield app


@pytest.fixture()
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    """Create a new test client for submitting HTTP requests."""
    with app.test_client() as client:
        yield client
