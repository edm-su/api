from datetime import timezone

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.post import NewPostDTO, Post
from app.internal.entity.user import User
from app.internal.usecase.repository.post import PostgresPostRepository


@pytest.fixture(scope="session")
def repository(
    pg_session: AsyncSession,
) -> PostgresPostRepository:
    return PostgresPostRepository(pg_session)

@pytest.fixture()
def new_post_data(
    faker: Faker,
    pg_user: User,
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
        user=pg_user,
    )

@pytest.fixture()
async def pg_post(
    faker: Faker,
    pg_user: User,
    repository: PostgresPostRepository,
) -> Post:
    post = NewPostDTO(
        title=faker.sentence(),
        text={"test": "test"},
        slug=faker.slug(),
        user=pg_user,
    )
    return await repository.create(post)

class TestPostgresPostRepository:
    async def test_get_by_slug(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        post = await repository.get_by_slug(pg_post.slug)

        assert isinstance(post, Post)
        assert post == pg_post

    async def test_get_all(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        posts = await repository.get_all()

        assert isinstance(posts, list)
        assert all(isinstance(post, (Post | type(None))) for post in posts)

    async def test_count(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        count = await repository.count()

        assert count > 0

    async def test_delete(
        self: Self,
        repository: PostgresPostRepository,
        pg_post: Post,
    ) -> None:
        old_count = await repository.count()
        result = await repository.delete(pg_post)
        new_count = await repository.count()

        assert result
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
