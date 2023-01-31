from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.internal.entity.user import User
from app.repositories.user_video import PostgresUserVideoRepository
from app.schemas.video import PgVideo
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_like_video(
    client: AsyncClient,
    pg_video: PgVideo,
    user: Mapping,
    pg_user_video_repository: PostgresUserVideoRepository,
) -> None:
    user = User(**user)
    headers = create_auth_header(user.username)
    url = f"/videos/{pg_video.slug}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await pg_user_video_repository.is_liked(user, pg_video)


@pytest.mark.asyncio
async def test_already_liked_video(
    client: AsyncClient,
    liked_video: PgVideo,
    admin: Mapping,
) -> None:
    headers = create_auth_header(admin["username"])
    url = f"/videos/{liked_video.slug}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_like_video_by_user(
    client: AsyncClient,
    pg_video: PgVideo,
    user: Mapping,
) -> None:
    headers = create_auth_header(user["username"])
    url = f"/videos/{pg_video.slug}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_like_video_unauthorized(
    client: AsyncClient,
    pg_video: PgVideo,
) -> None:
    url = f"/videos/{pg_video.slug}/like"
    response = await client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_unlike_video(
    client: AsyncClient,
    liked_video: PgVideo,
    admin: Mapping,
    pg_user_video_repository: PostgresUserVideoRepository,
) -> None:
    admin = User(**admin)
    headers = create_auth_header(admin.username)
    url = f"/videos/{liked_video.slug}/like"
    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await pg_user_video_repository.is_liked(admin, liked_video)


@pytest.mark.asyncio
async def test_unlike_already_unliked_video(
    client: AsyncClient,
    pg_video: PgVideo,
    admin: Mapping,
    pg_user_video_repository: PostgresUserVideoRepository,
) -> None:
    admin = User(**admin)
    headers = create_auth_header(admin.username)
    url = f"/videos/{pg_video.slug}/like"
    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert not await pg_user_video_repository.is_liked(admin, pg_video)


@pytest.mark.asyncio
async def test_unlike_video_unauthorized(
    client: AsyncClient,
    liked_video: PgVideo,
) -> None:
    url = f"/videos/{liked_video.slug}/like"
    response = await client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_liked_videos(
    client: AsyncClient,
    liked_video: PgVideo,
    admin: Mapping,
) -> None:
    headers = create_auth_header(admin["username"])
    response = await client.get("/users/liked_videos", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    response_videos = response.json()
    assert liked_video == PgVideo(**response_videos[0])


@pytest.mark.asyncio
async def test_liked_videos_by_guest(
    client: AsyncClient,
    liked_video: PgVideo,
) -> None:
    response = await client.get("/users/liked_videos")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
