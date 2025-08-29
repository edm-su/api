import pytest
from faker import Faker
from meilisearch_python_async import Client
from meilisearch_python_async.errors import MeilisearchApiError
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import (
    DeleteType,
    NewVideoDto,
    UpdateVideoDto,
    Video,
)
from edm_su_api.internal.usecase.exceptions.video import (
    VideoAlreadyDeletedError,
    VideoNotDeletedError,
    VideoNotFoundError,
)
from edm_su_api.internal.usecase.repository.user_videos import (
    PostgresUserVideosRepository,
)
from edm_su_api.internal.usecase.repository.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)

pytestmark = pytest.mark.anyio


class TestPostgresVideoRepository:
    @pytest.fixture
    def user_videos_repository(
        self, pg_session: AsyncSession
    ) -> PostgresUserVideosRepository:
        return PostgresUserVideosRepository(pg_session)

    @pytest.fixture
    def new_video_data(
        self: Self,
        faker: Faker,
    ) -> NewVideoDto:
        return NewVideoDto(
            title=faker.word(),
            date=faker.date_object(),
            yt_id=str(faker.uuid4()),
            yt_thumbnail=faker.url(),
            duration=faker.random_int(
                min=20 * 60,
                max=120 * 60,
            ),
            slug=faker.slug(),
            is_blocked_in_russia=True,
        )

    async def test_get_all(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> None:
        result = await pg_video_repository.get_all()

        assert isinstance(result, list)
        assert len(result) > 0
        assert pg_video in result

    async def test_get_by_slug(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> None:
        result = await pg_video_repository.get_by_slug(pg_video.slug)

        assert result == pg_video

    async def test_get_by_yt_id(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        result = await pg_video_repository.get_by_yt_id(pg_video.yt_id)

        assert result == pg_video

    async def test_get_by_id(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        result = await pg_video_repository.get_by_id(pg_video.id)

        assert result == pg_video

    async def test_create(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        new_video_data: NewVideoDto,
    ) -> None:
        result = await pg_video_repository.create(new_video_data)

        assert isinstance(result, Video)

        pg_video = await pg_video_repository.get_by_id(result.id)

        assert pg_video == result
        assert pg_video.is_blocked_in_russia == new_video_data.is_blocked_in_russia

    async def test_update(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        updated_data = UpdateVideoDto(**pg_video.model_dump())
        updated_data.title = "new title"
        result = await pg_video_repository.update(updated_data)

        assert result.title != pg_video.title

        video = await pg_video_repository.get_by_id(result.id)

        assert video == result

    async def test_delete(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        await pg_video_repository.delete(pg_video.id)

        with pytest.raises(VideoNotFoundError):
            _ = await pg_video_repository.get_by_id(pg_video.id)

    async def test_temporary_delete(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        await pg_video_repository.delete(pg_video.id, type_=DeleteType.TEMPORARY)

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_id(pg_video.id)

    async def test_get_all_with_favorite_mark(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
        user: User,
        user_videos_repository: PostgresUserVideosRepository,
    ) -> None:
        await user_videos_repository.like_video(user, pg_video)

        result = await pg_video_repository.get_all_with_favorite_mark(user.id)

        assert isinstance(result, list)
        assert len(result) > 0

        video = result[0]
        assert video.id == pg_video.id
        assert video.is_favorite is True

    async def test_get_by_slug_with_favorite_mark(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
        user: User,
        user_videos_repository: PostgresUserVideosRepository,
    ) -> None:
        await user_videos_repository.like_video(user, pg_video)

        result = await pg_video_repository.get_by_slug_with_favorite_mark(
            pg_video.slug, user.id
        )

        assert isinstance(result, Video)
        assert result.id == pg_video.id
        assert result.is_favorite is True

        await user_videos_repository.unlike_video(user, pg_video)
        result = await pg_video_repository.get_by_slug_with_favorite_mark(
            pg_video.slug, user.id
        )

        assert result.is_favorite is False

        with pytest.raises(VideoNotFoundError):
            _ = await pg_video_repository.get_by_slug_with_favorite_mark(
                "9999", user.id
            )

    @pytest.mark.usefixtures("pg_video")
    async def test_count(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
    ) -> None:
        result = await pg_video_repository.count()

        assert result > 0

    # Soft Delete Tests
    @pytest.fixture
    async def soft_deleted_video(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> Video:
        # Soft delete the video
        await pg_video_repository.delete(pg_video.id, type_=DeleteType.TEMPORARY)

        # Get the video with include_deleted=True
        return await pg_video_repository.get_by_id(pg_video.id, include_deleted=True)

    @pytest.fixture
    async def permanently_deleted_video(
        self: Self,
        pg_video: Video,
        pg_video_repository: PostgresVideoRepository,
    ) -> Video:
        # Permanently delete the video
        await pg_video_repository.delete(pg_video.id, type_=DeleteType.PERMANENT)

        # Get the video with include_deleted=True
        return pg_video

    async def test_get_all_with_include_deleted(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Should not include deleted videos by default
        videos = await pg_video_repository.get_all(limit=1000)
        assert not any(v.id == soft_deleted_video.id for v in videos)

        # Should include deleted videos when include_deleted=True
        videos_with_deleted = await pg_video_repository.get_all(
            limit=1000, include_deleted=True
        )

        # Check if the soft-deleted video is in the results
        assert any(v.id == soft_deleted_video.id for v in videos_with_deleted), (
            f"Video with ID {soft_deleted_video.id} not found in results"
        )

        # Verify the deleted video has the correct deletion status
        deleted_video = next(
            (v for v in videos_with_deleted if v.id == soft_deleted_video.id), None
        )
        assert deleted_video is not None
        assert deleted_video.deleted is True
        assert deleted_video.delete_type == DeleteType.TEMPORARY

    async def test_get_all_without_permanent_deleted(
        self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
        faker: Faker,
    ) -> None:
        # Given
        permanently_deleted_video = await pg_video_repository.create(
            NewVideoDto(
                title="Permanently deleted video",
                date=faker.past_date(),
                yt_id="permanently",
                yt_thumbnail=faker.image_url(),
                duration=20000,
            )
        )
        await pg_video_repository.delete(permanently_deleted_video.id)

        # When
        videos = await pg_video_repository.get_all(include_deleted=True)
        videos_ids = [video.id for video in videos]

        # Then
        assert permanently_deleted_video.id not in videos_ids
        assert soft_deleted_video.id in videos_ids

    async def test_get_all_with_favorite_mark_include_deleted(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
        user: User,
    ) -> None:
        # Should not include deleted videos by default
        videos = await pg_video_repository.get_all_with_favorite_mark(
            user.id, limit=1000
        )
        assert not any(v.id == soft_deleted_video.id for v in videos)

        # Should include deleted videos when include_deleted=True
        videos_with_deleted = await pg_video_repository.get_all_with_favorite_mark(
            user.id, limit=1000, include_deleted=True
        )

        assert any(v.id == soft_deleted_video.id for v in videos_with_deleted), (
            f"Video with ID {soft_deleted_video.id} not found in results"
        )

    async def test_get_by_methods_with_include_deleted(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
        user: User,
    ) -> None:
        # Should raise error when trying to get deleted video without include_deleted
        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_id(soft_deleted_video.id)

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_slug(soft_deleted_video.slug)

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_yt_id(soft_deleted_video.yt_id)

        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_slug_with_favorite_mark(
                soft_deleted_video.slug, user.id
            )

        # Should return the video when include_deleted=True
        video = await pg_video_repository.get_by_id(
            soft_deleted_video.id, include_deleted=True
        )
        assert video.id == soft_deleted_video.id
        assert video.deleted is True

        video = await pg_video_repository.get_by_slug(
            soft_deleted_video.slug, include_deleted=True
        )
        assert video.slug == soft_deleted_video.slug
        assert video.deleted is True

        video = await pg_video_repository.get_by_yt_id(
            soft_deleted_video.yt_id, include_deleted=True
        )
        assert video.yt_id == soft_deleted_video.yt_id
        assert video.deleted is True

        video = await pg_video_repository.get_by_slug_with_favorite_mark(
            soft_deleted_video.slug, user.id, include_deleted=True
        )
        assert video.slug == soft_deleted_video.slug
        assert video.deleted is True

    async def test_count_with_include_deleted(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Count without deleted videos
        count_without_deleted = await pg_video_repository.count()

        # Count with deleted videos
        count_with_deleted = await pg_video_repository.count(include_deleted=True)

        # Should have more videos when including deleted ones
        assert count_with_deleted > count_without_deleted

    async def test_restore_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Restore the video
        restored_video = await pg_video_repository.restore(soft_deleted_video.id)

        # Verify the video is restored
        assert restored_video.deleted is False
        assert restored_video.delete_type is None

        # Should be able to get the video without include_deleted now
        video = await pg_video_repository.get_by_id(restored_video.id)
        assert video.id == restored_video.id
        assert video.deleted is False
        assert video.delete_type is None

    async def test_restore_not_deleted_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        pg_video: Video,
    ) -> None:
        # Try to restore a video that's not deleted
        with pytest.raises(VideoNotDeletedError):
            await pg_video_repository.restore(pg_video.id)

    async def test_restore_permanently_deleted_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        permanently_deleted_video: Video,
    ) -> None:
        # Try to restore a permanently deleted video - should fail
        with pytest.raises(VideoNotDeletedError):
            await pg_video_repository.restore(permanently_deleted_video.id)

    async def test_restore_only_temporary_deleted_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Verify that only temporarily deleted videos can be restored
        assert soft_deleted_video.deleted is True
        assert soft_deleted_video.delete_type == DeleteType.TEMPORARY

        # This should succeed
        restored_video = await pg_video_repository.restore(soft_deleted_video.id)
        assert restored_video.deleted is False
        assert restored_video.delete_type is None

    async def test_delete_already_deleted_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Try to soft-delete an already soft-deleted video
        with pytest.raises(VideoAlreadyDeletedError):
            await pg_video_repository.delete(
                soft_deleted_video.id, type_=DeleteType.TEMPORARY
            )

    async def test_permanent_delete_soft_deleted_video(
        self: Self,
        pg_video_repository: PostgresVideoRepository,
        soft_deleted_video: Video,
    ) -> None:
        # Permanently delete a soft-deleted video (change type to permanent)
        await pg_video_repository.delete(
            soft_deleted_video.id, type_=DeleteType.PERMANENT
        )

        # Video should still exist but with permanent delete type
        with pytest.raises(VideoNotFoundError):
            await pg_video_repository.get_by_id(
                soft_deleted_video.id, include_deleted=True
            )


class TestMeilisearchVideoRepository:
    @pytest.fixture(scope="session")
    def repository(
        self: Self,
        ms_client: Client,
    ) -> MeilisearchVideoRepository:
        return MeilisearchVideoRepository(ms_client)

    @pytest.fixture
    async def ms_video(
        self: Self,
        repository: MeilisearchVideoRepository,
        pg_video: Video,
    ) -> Video:
        return await repository.create(pg_video)

    async def test_create(
        self: Self,
        pg_video: Video,
        repository: MeilisearchVideoRepository,
    ) -> None:
        result = await repository.create(pg_video)
        document = await repository.index.get_document(str(result.id))

        assert isinstance(result, Video)
        assert document
        assert document.get("is_blocked_in_russia") is None

    async def test_delete(
        self: Self,
        ms_video: Video,
        repository: MeilisearchVideoRepository,
    ) -> None:
        await repository.delete(ms_video.id)

        with pytest.raises(MeilisearchApiError):
            _ = await repository.index.get_document(str(ms_video.id))

    async def test_update(
        self,
        ms_video: Video,
        repository: MeilisearchVideoRepository,
    ) -> None:
        updated_data = UpdateVideoDto(**ms_video.model_dump())
        updated_data.title = "New title"
        await repository.update(ms_video.id, updated_data)

        document = await repository.index.get_document(str(ms_video.id))

        assert document
        assert updated_data.title == document.get("title")
