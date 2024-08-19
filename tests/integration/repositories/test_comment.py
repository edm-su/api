import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.comment import Comment, NewCommentDto
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.repository.comment import (
    PostgresCommentRepository,
)


@pytest.fixture
def repository(
    pg_session: AsyncSession,
) -> PostgresCommentRepository:
    return PostgresCommentRepository(pg_session)


@pytest.fixture
async def pg_comment(
    faker: Faker,
    user: User,
    repository: PostgresCommentRepository,
    pg_video: Video,
) -> Comment:
    comment = NewCommentDto(
        text=faker.sentence(),
        user=user,
        video=pg_video,
    )
    return await repository.create(comment)


@pytest.fixture
async def new_comment_data(
    faker: Faker,
    user: User,
    pg_video: Video,
) -> NewCommentDto:
    return NewCommentDto(
        text=faker.sentence(),
        user=user,
        video=pg_video,
    )


class TestPostgresCommentRepository:
    async def test_create(
        self: Self,
        repository: PostgresCommentRepository,
        new_comment_data: NewCommentDto,
    ) -> None:
        comment = await repository.create(new_comment_data)

        assert isinstance(comment, Comment)
        assert comment.text == new_comment_data.text

        assert comment in await repository.get_all()

    async def test_get_all(
        self: Self,
        repository: PostgresCommentRepository,
        pg_comment: Comment,
    ) -> None:
        comments = await repository.get_all()

        assert isinstance(comments, list)
        assert len(comments) >= 1
        assert pg_comment in comments

    async def test_count(
        self: Self,
        repository: PostgresCommentRepository,
        pg_comment: Comment,
    ) -> None:
        count = await repository.count()

        assert count > 0

    async def test_get_video_comments(
        self: Self,
        repository: PostgresCommentRepository,
        pg_comment: Comment,
    ) -> None:
        comments = await repository.get_video_comments(pg_comment.video_id)

        assert isinstance(comments, list)
        assert len(comments) > 0
        assert pg_comment in comments
