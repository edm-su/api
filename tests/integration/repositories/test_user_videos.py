import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.exceptions.user_videos import (
    UserVideoNotLikedError,
)
from edm_su_api.internal.usecase.repository.user_videos import (
    PostgresUserVideosRepository,
)


class TestPostgresUserVideosRepository:
    @pytest.fixture
    def repository(
        self: Self,
        pg_session: AsyncSession,
    ) -> PostgresUserVideosRepository:
        return PostgresUserVideosRepository(pg_session)

    @pytest.fixture
    async def like_video(
        self: Self,
        user: User,
        pg_video: Video,
        repository: PostgresUserVideosRepository,
    ) -> None:
        await repository.like_video(user, pg_video)

    async def test_like_video(
        self: Self,
        repository: PostgresUserVideosRepository,
        user: User,
        pg_video: Video,
    ) -> None:
        await repository.like_video(user, pg_video)

        response = await repository.is_liked(user, pg_video)
        assert response is True

    @pytest.mark.usefixtures("like_video")
    async def test_unlike_video(
        self: Self,
        repository: PostgresUserVideosRepository,
        user: User,
        pg_video: Video,
    ) -> None:
        await repository.unlike_video(user, pg_video)

        response = await repository.is_liked(user, pg_video)
        assert response is False

        with pytest.raises(UserVideoNotLikedError):
            await repository.unlike_video(user, pg_video)

    @pytest.mark.usefixtures("like_video")
    async def test_get_user_videos(
        self: Self,
        repository: PostgresUserVideosRepository,
        user: User,
        pg_video: Video,
    ) -> None:
        response = await repository.get_user_videos(user)

        assert len(response) > 0
        assert pg_video in response

    @pytest.mark.usefixtures("like_video")
    async def test_is_liked(
        self: Self,
        repository: PostgresUserVideosRepository,
        user: User,
        pg_video: Video,
    ) -> None:
        response = await repository.is_liked(user, pg_video)

        assert response is True

        await repository.unlike_video(user, pg_video)
        response = await repository.is_liked(user, pg_video)

        assert response is False
