from starlette.testclient import TestClient

from app.main import app
from app.tests.assertions import assert_valid_schema

client = TestClient(app)


def test_read_channels():
    response = client.get('/channels/')
    assert_valid_schema(response.json(), 'channels.json')
    assert response.status_code == 200
