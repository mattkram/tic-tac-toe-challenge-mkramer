import pytest
from flask.testing import FlaskClient


@pytest.mark.parametrize(
    "url,expected_status_code",
    [
        ("/", 200),
        ("/non-existent", 404),
    ],
)
def test_response_status_code(
    client: FlaskClient, url: str, expected_status_code: int
) -> None:
    """Check the client response status code for different routes."""
    response = client.get(url)
    assert response.status_code == expected_status_code
