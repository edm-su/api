from starlette import status

from app.schemas.video import Video
from app.tests.helpers import create_auth_header


def test_read_videos(client, videos):
    response = client.get('/videos/')

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers['x-total-count']) == len(videos)


def test_delete_video(client, videos, admin):
    headers = create_auth_header(admin['username'])
    response = client.delete(f"/videos/{videos[0]['slug']}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_read_video(client, videos):
    response = client.get(f"/videos/{videos[0]['slug']}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())


def test_read_related_videos(client, videos):
    response = client.get(f"/videos/{videos[0]['slug']}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)


def test_like_video(client, videos, admin):
    headers = create_auth_header(admin['username'])
    response = client.post(f"/videos/{videos[0]['slug']}/like", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_dislike_video(client, liked_video, admin):
    headers = create_auth_header(admin['username'])
    response = client.delete(f"/videos/{liked_video['slug']}/like", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_liked_videos(client, liked_video, admin):
    headers = create_auth_header(admin['username'])
    response = client.get('/users/liked_videos', headers=headers)

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert liked_video['slug'] in [video['slug'] for video in response.json()]
