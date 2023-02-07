from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from app.internal.entity.post import NewPostDTO, Post
from app.internal.entity.user import User
from app.internal.usecase.exceptions.video import (
    NotFoundException,
    SlugNotUniqueException,
)
from app.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostBySlugUseCase,
    GetPostCountUseCase,
)
from app.internal.usecase.repository.post import PostgresPostRepository


@pytest.fixture
def repository(mocker: MockerFixture) -> PostgresPostRepository:
    session = mocker.MagicMock()
    return PostgresPostRepository(session)


@pytest.fixture
def post(faker: Faker) -> Post:
    return Post(
        id=1,
        user_id=1,
        title=faker.sentence(),
        text={faker.sentence(): faker.sentence()},
        published_at=faker.future_datetime(tzinfo=timezone.utc),
        slug=faker.slug(),
        annotation=faker.paragraph(),
        thumbnail=faker.url(),
    )


@pytest.fixture
def new_post(faker: Faker, post: Post) -> NewPostDTO:
    return NewPostDTO(
        title=post.title,
        text=post.text,
        published_at=post.published_at,
        slug=post.slug,
        annotation=post.annotation,
        thumbnail=post.thumbnail,
        user=User(
            id=1,
            username=faker.user_name(),
            email=faker.email(),
            created=faker.past_datetime(tzinfo=timezone.utc),
        ),
    )


class TestCreatePostUseCase:
    @pytest.fixture(autouse=True)
    def mock(self, mocker: MockerFixture, faker: Faker, post: Post) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "create",
            return_value=post,
        )

    @pytest.fixture
    def usecase(self, repository: PostgresPostRepository) -> CreatePostUseCase:
        return CreatePostUseCase(repository)

    async def test_create_post(
        self,
        usecase: AsyncMock,
        post: Post,
        new_post: NewPostDTO,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=None,
        )
        assert await usecase.execute(new_post) == post

        usecase.repository.create: AsyncMock  # type: ignore
        usecase.repository.create.assert_awaited_once()

        usecase.repository.get_by_slug: AsyncMock  # type: ignore
        usecase.repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_create_post_with_duplicate_slug(
        self,
        usecase: AsyncMock,
        post: Post,
        new_post: NewPostDTO,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=post,
        )
        with pytest.raises(SlugNotUniqueException):
            await usecase.execute(new_post)

        usecase.repository.create.assert_not_awaited()


class TestGetAllPostsUseCase:
    @pytest.fixture(autouse=True)
    def mock(self, mocker: MockerFixture, faker: Faker) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_all",
            return_value=[
                Post(
                    id=1,
                    user_id=1,
                    title=faker.sentence(),
                    text={faker.sentence(): faker.sentence()},
                    published_at=faker.future_datetime(tzinfo=timezone.utc),
                    slug=faker.slug(),
                    annotation=faker.paragraph(),
                    thumbnail=faker.url(),
                ),
                Post(
                    id=2,
                    user_id=1,
                    title=faker.sentence(),
                    text={faker.sentence(): faker.sentence()},
                    published_at=faker.future_datetime(tzinfo=timezone.utc),
                    slug=faker.slug(),
                    annotation=faker.paragraph(),
                    thumbnail=faker.url(),
                ),
            ],
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresPostRepository,
    ) -> GetAllPostsUseCase:
        return GetAllPostsUseCase(repository)

    async def test_get_all_posts(
        self,
        usecase: AsyncMock,
    ) -> None:
        posts = await usecase.execute()
        assert len(posts) == 2

        usecase.repository.get_all.assert_awaited_once()


class TestGetPostBySlugUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresPostRepository,
    ) -> GetPostBySlugUseCase:
        return GetPostBySlugUseCase(repository)

    async def test_get_post_by_slug(
        self,
        usecase: AsyncMock,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=post,
        )
        assert await usecase.execute(post.slug) == post

        usecase.repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_get_post_by_slug_with_not_existing_slug(
        self,
        usecase: AsyncMock,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=None,
        )
        with pytest.raises(NotFoundException):
            await usecase.execute(post.slug)

        usecase.repository.get_by_slug.assert_awaited_once_with(post.slug)


class TestGetPostCountUseCase:
    @pytest.fixture(autouse=True)
    def mock(self, mocker: MockerFixture, faker: Faker) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "count",
            return_value=2,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresPostRepository,
    ) -> GetPostCountUseCase:
        return GetPostCountUseCase(repository)

    async def test_get_post_count(
        self,
        usecase: AsyncMock,
    ) -> None:
        assert await usecase.execute() == 2

        usecase.repository.count.assert_awaited_once()


class TestDeletePostUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresPostRepository,
    ) -> DeletePostUseCase:
        return DeletePostUseCase(repository)

    @pytest.fixture(autouse=True)
    def mock(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "delete",
            return_value=True,
        )

    async def test_delete_post(
        self,
        usecase: AsyncMock,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=post,
        )
        assert await usecase.execute(post.slug) is None

        usecase.repository.delete: AsyncMock  # type: ignore
        usecase.repository.delete.assert_awaited_once_with(post)

        usecase.repository.get_by_slug: AsyncMock  # type: ignore
        usecase.repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_delete_post_with_not_existing_slug(
        self,
        usecase: AsyncMock,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.post.PostgresPostRepository."
            "get_by_slug",
            return_value=None,
        )
        with pytest.raises(NotFoundException):
            await usecase.execute(post.slug)

        usecase.repository.delete: AsyncMock  # type: ignore
        usecase.repository.delete.assert_not_awaited()

        usecase.repository.get_by_slug.assert_awaited_once_with(post.slug)
