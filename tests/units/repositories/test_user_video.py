from typing import Mapping

import pytest

from app.repositories.user_video import PostgresUserVideoRepository
from app.schemas.user import User
from app.schemas.video import PgVideo


class TestPostgresUserVideoRepository:
    @pytest.mark.asyncio
    async def test_like_video(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        pg_video: PgVideo,
        user: Mapping,
    ) -> None:
        user = User(**user)
        assert await pg_user_video_repository.like_video(user, pg_video)
        assert await pg_user_video_repository.is_liked(user, pg_video)

    @pytest.mark.asyncio
    async def test_like_video_already_liked(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        liked_video: PgVideo,
        admin: Mapping,
    ) -> None:
        user = User(**admin)
        assert (
            await pg_user_video_repository.like_video(user, liked_video)
            is False
        )

    @pytest.mark.asyncio
    async def test_unlike_video(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        liked_video: PgVideo,
        admin: Mapping,
    ) -> None:
        user = User(**admin)
        assert (
            await pg_user_video_repository.unlike_video(user, liked_video)
            is True
        )
        assert (
            await pg_user_video_repository.is_liked(user, liked_video) is False
        )

    @pytest.mark.asyncio
    async def test_unlike_video_not_liked(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        user: Mapping,
        pg_video: PgVideo,
    ) -> None:
        user = User(**user)
        assert (
            await pg_user_video_repository.unlike_video(user, pg_video)
            is False
        )

    @pytest.mark.asyncio
    async def test_get_liked_videos(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        liked_video: PgVideo,
        admin: Mapping,
    ) -> None:
        user = User(**admin)
        assert await pg_user_video_repository.get_liked_videos(user)

    @pytest.mark.asyncio
    async def test_get_liked_videos_empty(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        user: Mapping,
    ) -> None:
        user = User(**user)
        assert await pg_user_video_repository.get_liked_videos(user) == []

    @pytest.mark.asyncio
    async def test_is_liked(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        liked_video: PgVideo,
        admin: Mapping,
    ) -> None:
        user = User(**admin)
        assert await pg_user_video_repository.is_liked(user, liked_video)

    @pytest.mark.asyncio
    async def test_is_liked_false(
        self,
        pg_user_video_repository: PostgresUserVideoRepository,
        user: Mapping,
        pg_video: PgVideo,
    ) -> None:
        user = User(**user)
        assert not await pg_user_video_repository.is_liked(user, pg_video)
