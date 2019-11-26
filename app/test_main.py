from starlette.testclient import TestClient

from app.main import app
from app.tests.assertions import assert_valid_schema

client = TestClient(app)


def test_read_channels():
    response = client.get('/channels/')
    assert_valid_schema(response.json(), 'channels.json')
    assert response.status_code == 200


def test_read_channel():
    response = client.get('/channels/united-music-events')
    assert_valid_schema(response.json(), 'channel.json')
    assert response.status_code == 200


def test_read_events():
    response = client.get('/events/')
    assert_valid_schema(response.json(), 'events.json')
    assert response.status_code == 200


def test_read_event():
    response = client.get('/events/25-years-of-bugged-out-x-printworks-london-2019')
    assert_valid_schema(response.json(), 'event.json')
    assert response.status_code == 200


def test_read_djs():
    response = client.get('/djs/')
    assert_valid_schema(response.json(), 'djs.json')
    assert response.status_code == 200


def test_read_dj():
    response = client.get('/djs/amc')
    assert_valid_schema(response.json(), 'dj.json')
    assert response.status_code == 200


def test_read_videos():
    response = client.get('/videos/')
    assert response.status_code == 200


def test_read_channel_videos():
    response = client.get('/channels/united-music-events/videos')
    assert response.status_code == 200


def test_read_video():
    response = client.get('/videos/dusky-live-at-25-years-of-bugged-out-x-printworks-london-2019')
    assert response.status_code == 200
