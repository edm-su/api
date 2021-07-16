from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import video as videos_crud
from app.schemas.video import Video
from tests.helpers import create_auth_header


##############################
# GET /videos/
##############################
@pytest.mark.asyncio
async def test_read_videos(client: AsyncClient, videos: Mapping) -> None:
    response = await client.get('/videos/')

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers['x-total-count']) == len(videos)


##############################
# DELETE /videos/:slug
##############################
@pytest.mark.asyncio
async def test_delete_video(
        client: AsyncClient,
        videos: Mapping,
        admin: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    response = await client.delete(
        f"/videos/{videos[0]['slug']}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await videos_crud.get_video_by_slug(videos[0]['slug'])


@pytest.mark.asyncio
async def test_delete_forbidden(
        client: AsyncClient,
        videos: Mapping,
        user: Mapping
) -> None:
    video = videos[0]
    response = await client.delete(f"/videos/{video['slug']}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await videos_crud.get_video_by_slug(video['slug'])

    auth_headers = create_auth_header(user['username'])
    response = await client.delete(
        f"/videos/{video['slug']}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await videos_crud.get_video_by_slug(video['slug'])


##############################
# GET /videos/:slug
##############################
@pytest.mark.asyncio
async def test_read_video(client: AsyncClient, videos: Mapping) -> None:
    response = await client.get(f"/videos/{videos[0]['slug']}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())


##############################
# GET /videos/:slug/related
##############################
@pytest.mark.asyncio
async def test_read_related_videos(
        client: AsyncClient,
        videos: Mapping,
) -> None:
    response = await client.get(f"/videos/{videos[0]['slug']}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)


##############################
# POST /videos/:slug/like
##############################
@pytest.mark.asyncio
async def test_like_video(
        client: AsyncClient,
        videos: Mapping,
        admin: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    url = f"/videos/{videos[0]['slug']}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


##############################
# DELETE /videos/:slug/like
##############################
@pytest.mark.asyncio
async def test_dislike_video(
        client: AsyncClient,
        liked_video: Mapping,
        admin: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    url = f"/videos/{liked_video['slug']}/like"
    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


##############################
# GET /users/liked_videos
##############################
@pytest.mark.asyncio
async def test_liked_videos(
        client: AsyncClient,
        liked_video: Mapping,
        admin: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    response = await client.get('/users/liked_videos', headers=headers)

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert liked_video['slug'] in [video['slug'] for video in response.json()]


@pytest.mark.asyncio
async def test_liked_videos_by_guest(
        client: AsyncClient,
        liked_video: Mapping,
) -> None:
    response = await client.get('/users/liked_videos')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
