from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.entity.comment import Comment, NewCommentDto
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.comment import (
    CreateCommentUseCase,
    GetAllCommentsUseCase,
    GetCountCommentsUseCase,
    GetVideoCommentsUseCase,
)
from app.internal.usecase.repository.comment import AbstractCommentRepository


@pytest.fixture()
def repository(mocker: MockerFixture) -> AbstractCommentRepository:
    return AsyncMock(AbstractCommentRepository)


@pytest.fixture()
def video(faker: Faker) -> Video:
    return Video(
        id=1,
        title=faker.pystr(),
        slug=faker.pystr(),
        duration=faker.pyint(),
        yt_id=faker.pystr(),
        yt_thumbnail=f"https://i.ytimg.com/vi/{faker.pystr()}/default.jpg",
        date=faker.date_between(
            start_date="-1y",
        ),
    )


@pytest.fixture()
def comment(
    faker: Faker,
    user: User,
    video: Video,
) -> Comment:
    return Comment(
        id=faker.pyint(min_value=1),
        user_id=user.id,
        video_id=video.id,
        text=faker.pystr(),
        published_at=faker.date_time_between(
            start_date="-1y",
        ),
    )


class TestCreateCommentUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        comment: Comment,
    ) -> None:
        repository.create.return_value = comment

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> CreateCommentUseCase:
        return CreateCommentUseCase(repository)

    async def test_create_comment(
        self: Self,
        usecase: CreateCommentUseCase,
        video: Video,
        user: User,
        comment: Comment,
        repository: AsyncMock,
    ) -> None:
        new_comment = await usecase.execute(
            NewCommentDto(
                text=comment.text,
                user=user,
                video=video,
            ),
        )
        assert new_comment.id == comment.id
        assert str(new_comment.user_id) == user.id
        assert new_comment.video_id == video.id
        assert new_comment.text == comment.text

        repository.create.assert_awaited_once()


class TestGetAllCommentsUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        comment: Comment,
    ) -> None:
        repository.get_all.return_value = [comment]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllCommentsUseCase:
        return GetAllCommentsUseCase(repository)

    async def test_get_all_comments(
        self: Self,
        usecase: GetAllCommentsUseCase,
        comment: Comment,
        repository: AsyncMock,
    ) -> None:
        comments = await usecase.execute()
        assert len(comments) == 1
        assert comments[0] == comment

        repository.get_all.assert_awaited_once()


class TestCountCommentsUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.count.return_value = 1

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetCountCommentsUseCase:
        return GetCountCommentsUseCase(repository)

    async def test_get_all_comments(
        self: Self,
        usecase: GetCountCommentsUseCase,
        repository: AsyncMock,
    ) -> None:
        count = await usecase.execute()
        assert count == 1

        repository.count.assert_awaited_once()


class TestGetVideoCommentsUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        comment: Comment,
    ) -> None:
        repository.get_video_comments.return_value = [comment]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetVideoCommentsUseCase:
        return GetVideoCommentsUseCase(repository)

    async def test_get_video_comments(
        self: Self,
        usecase: GetVideoCommentsUseCase,
        repository: AsyncMock,
        video: Video,
        comment: Comment,
        user: User,
    ) -> None:
        comments = await usecase.execute(video)
        assert len(comments) == 1
        assert comments[0] == comment

        repository.get_video_comments.assert_awaited_once_with(video.id)
