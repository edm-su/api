from starlette import status
from starlette.testclient import TestClient

from app.schemas.video import Video
from app.tests.helpers import create_auth_header


def test_read_videos(client: TestClient, videos):
    response = client.get('/videos/')

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers['x-total-count']) == len(videos)


def test_delete_video(client: TestClient, videos: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    response = client.delete(f"/videos/{videos[0]['slug']}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_read_video(client: TestClient, videos: dict):
    response = client.get(f"/videos/{videos[0]['slug']}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())


def test_read_related_videos(client: TestClient, videos: dict):
    response = client.get(f"/videos/{videos[0]['slug']}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)


def test_like_video(client: TestClient, videos: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    url = f"/videos/{videos[0]['slug']}/like"
    response = client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_dislike_video(client: TestClient, liked_video: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    url = f"/videos/{liked_video['slug']}/like"
    response = client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_liked_videos(client: TestClient, liked_video: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    response = client.get('/users/liked_videos', headers=headers)

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert liked_video['slug'] in [video['slug'] for video in response.json()]
