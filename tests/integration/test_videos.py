from typing import Mapping

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.meilisearch import ms_client
from tests.helpers import create_auth_header


class TestMeilisearchVideoRepository(MeilisearchVideoRepository):
    async def get_by_slug(self, slug: str) -> Video | None:
        result = await self.index.search(filter=f"slug = {slug}")
        if result.nb_hits == 0:
            return None
        return Video.parse_obj(result.hits[0])


def video_data(faker: Faker) -> NewVideoDto:
    return NewVideoDto(
        slug=faker.slug(),
        title=faker.sentence(),
        date=faker.date_between(
            start_date="-30d",
            end_date="today",
        ),
        yt_id=faker.pystr(),
        yt_thumbnail=faker.image_url(),
        duration=faker.pyint(),
    )


@pytest.fixture
async def setup_data(pg_session: AsyncSession, faker: Faker) -> list[Video]:
    videos = []
    for _ in range(5):
        video = video_data(faker)
        videos.append(await PostgresVideoRepository(pg_session).create(video))
    await pg_session.flush()
    await pg_session.commit()

    for video in videos:
        await MeilisearchVideoRepository(ms_client).create(video)
    return videos


@pytest.mark.asyncio
async def test_read_videos(
    client: AsyncClient,
    setup_data: list[Video],
) -> None:
    """Read videos."""
    response = await client.get("/videos")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers["x-total-count"]) == len(setup_data)


@pytest.mark.asyncio
async def test_create_video(
    client: AsyncClient,
    admin: Mapping,
    faker: Faker,
    pg_session: AsyncSession,
) -> None:
    """Create video."""
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/videos",
        data=video_data(faker).json(),
        headers=auth_headers,
    )

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert Video.validate(data)
    assert (
        await PostgresVideoRepository(pg_session).get_by_id(data["id"])
        is not None
    )
    assert (
        await TestMeilisearchVideoRepository(ms_client).get_by_slug(
            data["slug"]
        )
        is not None
    )


@pytest.mark.asyncio
async def test_create_video_forbidden(
    client: AsyncClient,
    user: Mapping,
    faker: Faker,
    pg_session: AsyncSession,
) -> None:
    """Create video forbidden."""
    video = video_data(faker)

    auth_headers = create_auth_header(user["username"])
    response = await client.post(
        "/videos",
        data=video.json(),
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await PostgresVideoRepository(pg_session).get_by_slug(
        video.slug
    )

    response = await client.post(
        "/videos",
        data=video.json(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not await PostgresVideoRepository(pg_session).get_by_slug(
        video.slug
    )


@pytest.mark.asyncio
async def test_video_already_exist(
    client: AsyncClient,
    admin: Mapping,
    setup_data: list[Video],
    faker: Faker,
) -> None:
    """Create video with unique params."""
    auth_headers = create_auth_header(admin["username"])
    video = video_data(faker)
    video.slug = setup_data[0].slug

    response = await client.post(
        "/videos",
        data=video.json(),
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    error = response.json()
    assert f"Video with slug {video.slug} already exists" in error["detail"]

    video.slug = faker.slug()
    video.yt_id = setup_data[0].yt_id

    response = await client.post(
        "/videos",
        data=video.json(),
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    error = response.json()
    assert f"Video with yt_id {video.yt_id} already exists" in error["detail"]


@pytest.mark.asyncio
async def test_delete_video(
    client: AsyncClient,
    setup_data: list[Video],
    admin: Mapping,
    pg_session: AsyncSession,
) -> None:
    """Delete video."""
    headers = create_auth_header(admin["username"])
    video = setup_data[0]
    response = await client.delete(
        f"/videos/{video.slug}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert (
        await PostgresVideoRepository(pg_session).get_by_id(video.id) is None
    )
    assert (
        await TestMeilisearchVideoRepository(ms_client).get_by_slug(video.slug)
        is None
    )


@pytest.mark.asyncio
async def test_delete_video_forbidden(
    client: AsyncClient,
    setup_data: list[Video],
    user: Mapping,
    pg_session: AsyncSession,
) -> None:
    """Delete video forbidden."""
    auth_headers = create_auth_header(user["username"])
    video = setup_data[0]
    response = await client.delete(
        f"/videos/{video.slug}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert (
        await PostgresVideoRepository(pg_session).get_by_id(video.id)
        is not None
    )
    assert (
        await TestMeilisearchVideoRepository(ms_client).get_by_slug(video.slug)
        is not None
    )

    response = await client.delete(
        f"/videos/{video.slug}",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        await PostgresVideoRepository(pg_session).get_by_id(video.id)
        is not None
    )


@pytest.mark.asyncio
async def test_read_video(
    client: AsyncClient,
    setup_data: list[Video],
    pg_session: AsyncSession,
) -> None:
    response = await client.get(f"/videos/{setup_data[0].slug}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())
    assert (
        await PostgresVideoRepository(pg_session).get_by_id(setup_data[0].id)
        is not None
    )


@pytest.mark.asyncio
async def test_read_related_videos(
    client: AsyncClient,
    setup_data: list[Video],
) -> None:
    response = await client.get(f"/videos/{setup_data[0].slug}/related")

    assert response.status_code == status.HTTP_404_NOT_FOUND
