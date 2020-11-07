import pytest
from httpx import AsyncClient
from starlette import status

from app.schemas.video import Video
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_read_videos(client: AsyncClient, videos):
    response = await client.get('/videos/')

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers['x-total-count']) == len(videos)


@pytest.mark.asyncio
async def test_delete_video(client: AsyncClient, videos: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    response = await client.delete(
        f"/videos/{videos[0]['slug']}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_read_video(client: AsyncClient, videos: dict):
    response = await client.get(f"/videos/{videos[0]['slug']}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())


@pytest.mark.asyncio
async def test_read_related_videos(client: AsyncClient, videos: dict):
    response = await client.get(f"/videos/{videos[0]['slug']}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)


@pytest.mark.asyncio
async def test_like_video(client: AsyncClient, videos: dict, admin: dict):
    headers = create_auth_header(admin['username'])
    url = f"/videos/{videos[0]['slug']}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_dislike_video(
        client: AsyncClient,
        liked_video: dict,
        admin: dict,
):
    headers = create_auth_header(admin['username'])
    url = f"/videos/{liked_video['slug']}/like"
    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_liked_videos(
        client: AsyncClient,
        liked_video: dict,
        admin: dict,
):
    headers = create_auth_header(admin['username'])
    response = await client.get('/users/liked_videos', headers=headers)

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert liked_video['slug'] in [video['slug'] for video in response.json()]
