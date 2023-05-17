from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from typing_extensions import Self

from app.helpers import Paginator
from app.internal.entity.post import NewPostDTO, Post
from app.internal.entity.user import User
from app.internal.usecase.exceptions.post import PostNotFoundError
from app.internal.usecase.exceptions.video import (
    SlugNotUniqueError,
)
from app.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostBySlugUseCase,
    GetPostCountUseCase,
)
from app.internal.usecase.repository.post import AbstractPostRepository


@pytest.fixture()
def repository() -> AbstractPostRepository:
    return AsyncMock(repr=AbstractPostRepository)


@pytest.fixture()
def post(
    faker: Faker,
    user: User,
) -> Post:
    return Post(
        id=faker.random_int(),
        user_id=user.id,
        title=faker.sentence(),
        text={faker.sentence(): faker.sentence()},
        published_at=faker.future_datetime(tzinfo=timezone.utc),
        slug=faker.slug(),
        annotation=faker.paragraph(),
        thumbnail=faker.url(),
    )


@pytest.fixture()
def new_post(
    post: Post,
    user: User,
) -> NewPostDTO:
    return NewPostDTO(
        title=post.title,
        text=post.text,
        published_at=post.published_at,
        slug=post.slug,
        annotation=post.annotation,
        thumbnail=post.thumbnail,
        user=user,
    )


@pytest.fixture()
def user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
    )


class TestCreatePostUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.create.return_value = post

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AbstractPostRepository,
    ) -> CreatePostUseCase:
        return CreatePostUseCase(repository)

    async def test_create_post(
        self: Self,
        usecase: CreatePostUseCase,
        repository: AsyncMock,
        post: Post,
        new_post: NewPostDTO,
    ) -> None:
        repository.get_by_slug.return_value = None

        assert await usecase.execute(new_post) == post

        repository.create.assert_awaited_once()  # type: ignore[attr-defined]

        repository.get_by_slug.assert_awaited_once_with(post.slug)  # type: ignore[attr-defined]  # noqa: E501

    async def test_create_post_with_duplicate_slug(
        self: Self,
        usecase: CreatePostUseCase,
        post: Post,
        new_post: NewPostDTO,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = post

        with pytest.raises(SlugNotUniqueError):
            await usecase.execute(new_post)

        repository.create.assert_not_awaited()  # type: ignore[attr-defined]


class TestGetAllPostsUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        faker: Faker,
        post: Post,
    ) -> None:
        repository.get_all.return_value = [post]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllPostsUseCase:
        return GetAllPostsUseCase(repository)

    async def test_get_all_posts(
        self: Self,
        usecase: GetAllPostsUseCase,
        repository: AsyncMock,
    ) -> None:
        posts = await usecase.execute(paginator=Paginator())
        assert len(posts) == 1

        repository.get_all.assert_awaited_once()  # type: ignore[attr-defined]


class TestGetPostBySlugUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetPostBySlugUseCase:
        return GetPostBySlugUseCase(repository)

    async def test_get_post_by_slug(
        self: Self,
        usecase: GetPostBySlugUseCase,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = post

        assert await usecase.execute(post.slug) == post

        repository.get_by_slug.assert_awaited_once_with(post.slug)  # type: ignore[attr-defined]  # noqa: E501

    async def test_get_post_by_slug_with_not_existing_slug(
        self: Self,
        usecase: GetPostBySlugUseCase,
        repository: AsyncMock,
        post: Post,
    ) -> None:
        repository.get_by_slug.return_value = None

        with pytest.raises(PostNotFoundError):
            await usecase.execute(post.slug)

        repository.get_by_slug.assert_awaited_once_with(post.slug)  # type: ignore[attr-defined]  # noqa: E501


class TestGetPostCountUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.count.return_value = 2

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetPostCountUseCase:
        return GetPostCountUseCase(repository)

    async def test_get_post_count(
        self: Self,
        usecase: GetPostCountUseCase,
        repository: AsyncMock,
    ) -> None:
        assert await usecase.execute() == 2  # noqa: PLR2004

        repository.count.assert_awaited_once()  # type: ignore[attr-defined]


class TestDeletePostUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> DeletePostUseCase:
        return DeletePostUseCase(repository)

    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.delete.return_value = True

    async def test_delete_post(
        self: Self,
        usecase: DeletePostUseCase,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = post

        await usecase.execute(post.slug)

        repository.delete.assert_awaited_once_with(post)  # type: ignore[attr-defined]  # noqa: E501

        repository.get_by_slug.assert_awaited_once_with(post.slug)  # type: ignore[attr-defined]  # noqa: E501

    async def test_delete_post_with_not_existing_slug(
        self: Self,
        usecase: DeletePostUseCase,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = None

        with pytest.raises(PostNotFoundError):
            await usecase.execute(post.slug)

        repository.delete.assert_not_awaited()  # type: ignore[attr-defined]

        repository.get_by_slug.assert_awaited_once_with(post.slug)  # type: ignore[attr-defined]  # noqa: E501
