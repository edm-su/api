from collections.abc import Mapping

import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app.repositories.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.schemas.video import MeilisearchVideo, PgVideo
from tests.helpers import create_auth_header


@pytest.mark.asyncio()
async def test_read_videos(
    client: AsyncClient,
    videos: Mapping,
) -> None:
    response = await client.get("/videos")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert PgVideo.validate(video)
    assert int(response.headers["x-total-count"]) == len(videos)


@pytest.mark.asyncio()
async def test_create_video(
    client: AsyncClient,
    admin: Mapping,
    video_data: Mapping,
    ms_video_repository: MeilisearchVideoRepository,
    pg_video_repository: PostgresVideoRepository,
) -> None:
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/videos",
        json=video_data,
        headers=auth_headers,
    )

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert PgVideo.validate(data)
    assert await pg_video_repository.get_by_slug(data["slug"])
    assert await ms_video_repository.get_by_id(data["id"])


@pytest.mark.asyncio()
async def test_create_video_forbidden(
    client: AsyncClient,
    user: Mapping,
    video_data: Mapping,
    pg_video_repository: PostgresVideoRepository,
) -> None:
    slug = slugify(
        video_data["title"],
    )

    auth_headers = create_auth_header(user["username"])
    response = await client.post(
        "/videos",
        json=video_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await pg_video_repository.get_by_slug(slug)


@pytest.mark.asyncio()
async def test_create_video_unauthorized(
    client: AsyncClient,
    video_data: Mapping,
    pg_video_repository: PostgresVideoRepository,
) -> None:
    response = await client.post("/videos", json=video_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    slug = slugify(
        video_data["title"],
    )
    assert not await pg_video_repository.get_by_slug(
        slug,
    )


@pytest.mark.asyncio()
async def test_video_already_exist(
    client: AsyncClient,
    admin: Mapping,
    videos: Mapping,
) -> None:
    auth_headers = create_auth_header(admin["username"])
    video = dict(videos[0])
    video["date"] = video["date"].strftime("%Y-%m-%d")

    response = await client.post(
        "/videos",
        json=video,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    error = response.json()
    assert "Такой slug уже занят" in error["detail"]
    assert "Такой yt_id уже существует" in error["detail"]


@pytest.mark.asyncio()
async def test_delete_video(  # noqa: PLR0913
    client: AsyncClient,
    pg_video: PgVideo,
    ms_video: MeilisearchVideo,
    ms_video_repository: MeilisearchVideoRepository,
    pg_video_repository: PostgresVideoRepository,
    admin: Mapping,
) -> None:
    headers = create_auth_header(admin["username"])
    response = await client.delete(
        f"/videos/{pg_video.slug}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await pg_video_repository.get_by_id(pg_video.id) is None
    assert await ms_video_repository.get_by_id(ms_video.id) is None


@pytest.mark.asyncio()
async def test_delete_video_forbidden(  # noqa: PLR0913
    client: AsyncClient,
    pg_video: PgVideo,
    ms_video: MeilisearchVideo,
    user: Mapping,
    ms_video_repository: MeilisearchVideoRepository,
    pg_video_repository: PostgresVideoRepository,
) -> None:
    auth_headers = create_auth_header(user["username"])
    response = await client.delete(
        f"/videos/{pg_video.slug}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await pg_video_repository.get_by_id(pg_video.id)
    assert await ms_video_repository.get_by_id(ms_video.id)


@pytest.mark.asyncio()
async def test_delete_video_unauthorized(
    client: AsyncClient,
    pg_video: PgVideo,
    ms_video: MeilisearchVideo,
    ms_video_repository: MeilisearchVideoRepository,
    pg_video_repository: PostgresVideoRepository,
) -> None:
    response = await client.delete(f"/videos/{pg_video.slug}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await pg_video_repository.get_by_id(pg_video.id)
    assert await ms_video_repository.get_by_id(ms_video.id)


@pytest.mark.asyncio()
async def test_read_video(
    client: AsyncClient,
    pg_video: PgVideo,
) -> None:
    response = await client.get(f"/videos/{pg_video.slug}")

    assert response.status_code == status.HTTP_200_OK
    assert PgVideo.validate(response.json())


@pytest.mark.asyncio()
async def test_read_related_videos(
    client: AsyncClient,
    pg_video: PgVideo,
) -> None:
    response = await client.get(f"/videos/{pg_video.slug}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert PgVideo.validate(video)
