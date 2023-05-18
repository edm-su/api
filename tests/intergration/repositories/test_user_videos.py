import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.repository.user_videos import (
    PostgresUserVideosRepository,
)


class TestPostgresUserVideosRepository:
    @pytest.fixture()
    def repository(
        self: Self,
        pg_session: AsyncSession,
    ) -> PostgresUserVideosRepository:
        return PostgresUserVideosRepository(pg_session)

    @pytest.fixture()
    async def _like_video(
        self: Self,
        pg_user: User,
        pg_video: Video,
        repository: PostgresUserVideosRepository,
    ) -> None:
        await repository.like_video(pg_user, pg_video)

    async def test_like_video(
        self: Self,
        repository: PostgresUserVideosRepository,
        pg_user: User,
        pg_video: Video,
    ) -> None:
        await repository.like_video(pg_user, pg_video)

        response = await repository.is_liked(pg_user, pg_video)
        assert response is True

    @pytest.mark.usefixtures("_like_video")
    async def test_unlike_video(
        self: Self,
        repository: PostgresUserVideosRepository,
        pg_user: User,
        pg_video: Video,
    ) -> None:
        await repository.unlike_video(pg_user, pg_video)

        response = await repository.is_liked(pg_user, pg_video)
        assert response is False

    @pytest.mark.usefixtures("_like_video")
    async def test_get_user_videos(
        self: Self,
        repository: PostgresUserVideosRepository,
        pg_user: User,
        pg_video: Video,
    ) -> None:
        response = await repository.get_user_videos(pg_user)

        assert len(response) == 1
        assert response[0] == pg_video

        await repository.unlike_video(pg_user, pg_video)
        response = await repository.get_user_videos(pg_user)

        assert len(response) == 0

    @pytest.mark.usefixtures("_like_video")
    async def test_is_liked(
        self: Self,
        repository: PostgresUserVideosRepository,
        pg_user: User,
        pg_video: Video,
    ) -> None:
        response = await repository.is_liked(pg_user, pg_video)

        assert response is True

        await repository.unlike_video(pg_user, pg_video)
        response = await repository.is_liked(pg_user, pg_video)

        assert response is False
