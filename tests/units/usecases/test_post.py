from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockFixture
from typing_extensions import Self

from edm_su_api.internal.entity.post import NewPostDTO, Post
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from edm_su_api.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostBySlugUseCase,
    GetPostCountUseCase,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
)
from edm_su_api.internal.usecase.repository.post import AbstractPostRepository


@pytest.fixture
def repository() -> AbstractPostRepository:
    return AsyncMock(repr=AbstractPostRepository)


@pytest.fixture
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


@pytest.fixture
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


class TestCreatePostUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.create.return_value = post

    @pytest.fixture
    def mock_permissions(self: Self, mocker: MockFixture) -> None:
        mocker.patch(
            "edm_su_api.internal.usecase.video.CreateVideoUseCase._set_permissions",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AbstractPostRepository,
        permissions_repo: AbstractPermissionRepository,
    ) -> CreatePostUseCase:
        return CreatePostUseCase(repository, permissions_repo)

    async def test_create_post(
        self: Self,
        usecase: CreatePostUseCase,
        repository: AsyncMock,
        post: Post,
        new_post: NewPostDTO,
    ) -> None:
        repository.get_by_slug.side_effect = PostNotFoundError

        assert await usecase.execute(new_post) == post

        repository.create.assert_awaited_once()

        repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_create_post_with_duplicate_slug(
        self: Self,
        usecase: CreatePostUseCase,
        post: Post,
        new_post: NewPostDTO,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = post

        with pytest.raises(PostSlugNotUniqueError):
            await usecase.execute(new_post)

        repository.create.assert_not_awaited()


class TestGetAllPostsUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
        faker: Faker,
        post: Post,
    ) -> None:
        repository.get_all.return_value = [post]

    @pytest.fixture
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
        posts = await usecase.execute()
        assert len(posts) == 1

        repository.get_all.assert_awaited_once()


class TestGetPostBySlugUseCase:
    @pytest.fixture
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

        repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_get_post_by_slug_with_not_existing_slug(
        self: Self,
        usecase: GetPostBySlugUseCase,
        repository: AsyncMock,
        post: Post,
    ) -> None:
        repository.get_by_slug.return_value = None

        with pytest.raises(PostNotFoundError):
            await usecase.execute(post.slug)

        repository.get_by_slug.assert_awaited_once_with(post.slug)


class TestGetPostCountUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.count.return_value = 1

    @pytest.fixture
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
        assert await usecase.execute() == 1

        repository.count.assert_awaited_once()


class TestDeletePostUseCase:
    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
        permissions_repo: AsyncMock,
    ) -> DeletePostUseCase:
        return DeletePostUseCase(repository, permissions_repo)

    @pytest.fixture(autouse=True)
    def mock(
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

        repository.delete.assert_awaited_once_with(post)

        repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_delete_post_with_not_existing_slug(
        self: Self,
        usecase: DeletePostUseCase,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.side_effect = PostNotFoundError

        with pytest.raises(PostNotFoundError):
            await usecase.execute(post.slug)

        repository.delete.assert_not_awaited()

        repository.get_by_slug.assert_awaited_once_with(post.slug)

    async def test_post_was_not_deleted(
        self: Self,
        usecase: DeletePostUseCase,
        post: Post,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = post
        repository.delete.side_effect = PostNotFoundError

        with pytest.raises(PostNotFoundError):
            await usecase.execute(post.slug)
        repository.delete.assert_awaited_once()
        repository.get_by_slug.assert_awaited_once_with(post.slug)
