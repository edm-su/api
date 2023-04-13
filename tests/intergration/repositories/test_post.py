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

class TestPostgresPostRepository:
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
