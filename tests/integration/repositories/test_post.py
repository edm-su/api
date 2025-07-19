from datetime import datetime, timezone
from uuid import UUID

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.post import (
    NewPostDTO,
    Post,
    PostEditHistory,
    UpdatePostDTO,
)
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.usecase.exceptions.post import PostNotFoundError
from edm_su_api.internal.usecase.repository.post import (
    PostgresPostHistoryRepository,
    PostgresPostRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository(
    pg_session: AsyncSession,
) -> PostgresPostRepository:
    return PostgresPostRepository(pg_session)


@pytest.fixture
def new_post_data(
    faker: Faker,
    user: User,
) -> NewPostDTO:
    return NewPostDTO(
        title=faker.sentence(),
        text={"test": "test"},
        slug=faker.slug(),
        published_at=faker.date_time_between(
            start_date="now",
            end_date="+1d",
            tzinfo=timezone.utc,
        ),
        user=user,
    )


@pytest.fixture
async def pg_post(
    new_post_data: NewPostDTO,
    repository: PostgresPostRepository,
) -> Post:
    new_post_data.published_at = datetime.now(tz=timezone.utc)
    return await repository.create(new_post_data)


class TestPostgresPostRepository:
    async def test_get_by_slug(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        post = await repository.get_by_slug(pg_post.slug)

        assert isinstance(post, Post)
        assert post == pg_post

    @pytest.mark.usefixtures("pg_post")
    async def test_get_all(
        self: Self,
        repository: PostgresPostRepository,
    ) -> None:
        posts = await repository.get_all()

        assert isinstance(posts, list)
        assert all(isinstance(post, (Post | type(None))) for post in posts)

    @pytest.mark.usefixtures("pg_post")
    async def test_count(
        self: Self,
        repository: PostgresPostRepository,
    ) -> None:
        count = await repository.count()

        assert count > 0

    async def test_delete(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        old_count = await repository.count()
        await repository.delete(pg_post)
        new_count = await repository.count()

        assert old_count - 1 == new_count

    async def test_create(
        self: Self,
        repository: PostgresPostRepository,
        new_post_data: NewPostDTO,
    ) -> None:
        post = await repository.create(new_post_data)

        assert isinstance(post, Post)
        assert post.title == new_post_data.title
        assert post.text == new_post_data.text
        assert post.slug == new_post_data.slug
        assert post.published_at == new_post_data.published_at


class TestPostgresRepositoryBoundary:
    async def test_get_by_wrong_slug(
        self: Self,
        repository: PostgresPostRepository,
    ) -> None:
        with pytest.raises(PostNotFoundError):
            await repository.get_by_slug("wrong_slug")

    async def test_delete_not_found(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        pg_post.id = 999_999
        with pytest.raises(PostNotFoundError):
            await repository.delete(pg_post)

    async def test_update_without_history(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
        user: User,
    ) -> None:
        update_data = UpdatePostDTO(
            title="Updated Title",
            annotation="Updated annotation",
            text={"updated": "content"},
            user=user,
            save_history=False,
        )

        updated_post = await repository.update(pg_post.id, update_data)

        assert isinstance(updated_post, Post)
        assert updated_post.id == pg_post.id
        assert updated_post.title == "Updated Title"
        assert updated_post.annotation == "Updated annotation"
        assert updated_post.text == {"updated": "content"}
        assert updated_post.updated_at is not None
        assert str(updated_post.updated_by) == user.id

    async def test_update_with_history(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
        user: User,
    ) -> None:
        update_data = UpdatePostDTO(
            title="Updated with History",
            user=user,
            save_history=True,
            history_description="Post title updated",
        )

        updated_post = await repository.update(pg_post.id, update_data)

        assert isinstance(updated_post, Post)
        assert updated_post.title == "Updated with History"
        assert updated_post.updated_at is not None
        assert str(updated_post.updated_by) == user.id

    async def test_update_non_existing_post(
        self: Self,
        repository: PostgresPostRepository,
        user: User,
    ) -> None:
        update_data = UpdatePostDTO(
            title="Should fail",
            user=user,
        )

        with pytest.raises(PostNotFoundError):
            await repository.update(999999, update_data)


@pytest.fixture
def history_repository(
    pg_session: AsyncSession,
) -> PostgresPostHistoryRepository:
    return PostgresPostHistoryRepository(pg_session)


class TestPostgresPostHistoryRepository:
    async def test_create_history_entry(
        self: Self,
        history_repository: PostgresPostHistoryRepository,
        pg_post: Post,
        user: User,
    ) -> None:
        history_entry = await history_repository.create(
            post_id=pg_post.id,
            description="Исправлены опечатки",
            edited_by=UUID(user.id),
        )

        assert isinstance(history_entry, PostEditHistory)
        assert history_entry.post_id == pg_post.id
        assert history_entry.description == "Исправлены опечатки"
        assert str(history_entry.edited_by) == user.id
        assert history_entry.edited_at is not None
        assert history_entry.id > 0

    async def test_get_post_history(
        self: Self,
        history_repository: PostgresPostHistoryRepository,
        pg_post: Post,
        user: User,
    ) -> None:
        await history_repository.create(
            post_id=pg_post.id,
            description="Первое изменение",
            edited_by=UUID(user.id),
        )
        await history_repository.create(
            post_id=pg_post.id,
            description="Второе изменение",
            edited_by=UUID(user.id),
        )

        history = await history_repository.get_by_post_id(pg_post.id)

        assert isinstance(history, list)
        assert len(history) == 2
        descriptions = [h.description for h in history]
        assert "Первое изменение" in descriptions
        assert "Второе изменение" in descriptions
        assert all(isinstance(entry, PostEditHistory) for entry in history)

    async def test_get_empty_history(
        self: Self,
        history_repository: PostgresPostHistoryRepository,
        pg_post: Post,
    ) -> None:
        history = await history_repository.get_by_post_id(pg_post.id)

        assert isinstance(history, list)
        assert len(history) == 0

    async def test_cascade_delete_history(
        self: Self,
        repository: PostgresPostRepository,
        history_repository: PostgresPostHistoryRepository,
        pg_post: Post,
        user: User,
    ) -> None:
        await history_repository.create(
            post_id=pg_post.id,
            description="Тестовое изменение",
            edited_by=UUID(user.id),
        )

        history = await history_repository.get_by_post_id(pg_post.id)
        assert len(history) == 1

        await repository.delete(pg_post)

        history_after_delete = await history_repository.get_by_post_id(pg_post.id)
        assert len(history_after_delete) == 0
