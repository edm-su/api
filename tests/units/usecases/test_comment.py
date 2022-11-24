from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from app.internal.entity.comment import Comment, NewCommentDto
from app.internal.entity.video import Video
from app.internal.usecase.comment import (
    CreateCommentUseCase,
    GetAllCommentsUseCase,
    GetCountCommentsUseCase,
)
from app.internal.usecase.repository.comment import (
    AbstractCommentRepository,
    PostgresCommentRepository,
)


@pytest.fixture
def repository(mocker: MockerFixture) -> PostgresCommentRepository:
    session = mocker.MagicMock()
    return PostgresCommentRepository(session)


@pytest.fixture
def video(faker: Faker) -> Video:
    return Video(
        id=1,
        title=faker.pystr(),
        slug=faker.pystr(),
        duration=faker.pyint(),
        yt_id=faker.pystr(),
        yt_thumbnail=f"https://i.ytimg.com/vi/{faker.pystr()}" f"/default.jpg",
        date=faker.date_between(
            start_date="-1y",
            end_date="today",
        ),
    )


class TestCreateCommentUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.comment"
            ".PostgresCommentRepository.create",
            return_value=Comment(
                id=1,
                user_id=1,
                video_id=1,
                text="test",
                published_at=datetime.now(),
            ),
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractCommentRepository,
    ) -> CreateCommentUseCase:
        return CreateCommentUseCase(repository)

    async def test_create_comment(
        self,
        usecase: CreateCommentUseCase,
        video: Video,
    ) -> None:
        comment = await usecase.execute(
            NewCommentDto(
                text="test",
                user_id=1,
                video=video,
            )
        )
        assert comment.id == 1
        assert comment.user_id == 1
        assert comment.video_id == 1
        assert comment.text == "test"

        usecase.repository.create: AsyncMock  # type: ignore
        usecase.repository.create.assert_awaited_once()


class TestGetAllCommentsUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.comment"
            ".PostgresCommentRepository.get_all",
            return_value=[
                Comment(
                    id=1,
                    user_id=1,
                    video_id=1,
                    text="test",
                    published_at=datetime.now(),
                )
            ],
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractCommentRepository,
    ) -> GetAllCommentsUseCase:
        return GetAllCommentsUseCase(repository)

    async def test_get_all_comments(
        self,
        usecase: GetAllCommentsUseCase,
    ) -> None:
        comments = await usecase.execute()
        assert len(comments) == 1
        assert comments[0].id == 1
        assert comments[0].user_id == 1
        assert comments[0].video_id == 1
        assert comments[0].text == "test"

        usecase.repository.get_all: AsyncMock  # type: ignore
        usecase.repository.get_all.assert_awaited_once()


class TestCountCommentsUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.comment"
            ".PostgresCommentRepository.count",
            return_value=1,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractCommentRepository,
    ) -> GetCountCommentsUseCase:
        return GetCountCommentsUseCase(repository)

    async def test_get_all_comments(
        self,
        usecase: GetCountCommentsUseCase,
    ) -> None:
        count = await usecase.execute()
        assert count == 1

        usecase.repository.count: AsyncMock  # type: ignore
        usecase.repository.count.assert_awaited_once()


class GetVideoCommentsUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository"
            ".comment.PostgresCommentRepository.get_all",
            return_value=[
                Comment(
                    id=1,
                    user_id=1,
                    video_id=1,
                    text="test",
                    published_at=datetime.now(),
                )
            ],
        )

    @pytest.fixture
    def usecase(
        self,
        repository: AbstractCommentRepository,
    ) -> GetAllCommentsUseCase:
        return GetAllCommentsUseCase(repository)

    async def test_get_all_comments(
        self,
        usecase: GetAllCommentsUseCase,
    ) -> None:
        comments = await usecase.execute()
        assert len(comments) == 1
        assert comments[0].id == 1
        assert comments[0].user_id == 1
        assert comments[0].video_id == 1
        assert comments[0].text == "test"

        usecase.repository.get_all: AsyncMock  # type: ignore
        usecase.repository.get_all.assert_awaited_once()
