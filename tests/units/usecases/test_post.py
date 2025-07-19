from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from faker import Faker
from pytest_mock import MockFixture
from typing_extensions import Self

from edm_su_api.internal.entity.post import (
    NewPostDTO,
    Post,
    PostEditHistory,
    UpdatePost,
    UpdatePostDTO,
)
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
    GetPostHistoryUseCase,
    UpdatePostUseCase,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
)
from edm_su_api.internal.usecase.repository.post import (
    AbstractPostHistoryRepository,
    AbstractPostRepository,
)

pytestmark = pytest.mark.anyio


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


@pytest.fixture
def history_repository() -> AbstractPostHistoryRepository:
    return AsyncMock(spec=AbstractPostHistoryRepository)


@pytest.fixture
def update_post_data(
    faker: Faker,
) -> UpdatePost:
    return UpdatePost(
        title=faker.sentence(),
        annotation=faker.paragraph(),
        text={faker.word(): faker.sentence()},
        thumbnail=faker.url(),
        published_at=faker.future_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture
def update_post_dto(
    update_post_data: UpdatePost,
    user: User,
) -> UpdatePostDTO:
    return UpdatePostDTO(
        **update_post_data.model_dump(exclude_unset=True),
        user=user,
        save_history=False,
    )


@pytest.fixture
def post_edit_history(
    faker: Faker,
    post: Post,
    user: User,
) -> PostEditHistory:
    return PostEditHistory(
        id=faker.random_int(),
        post_id=post.id,
        edited_at=faker.past_datetime(tzinfo=timezone.utc),
        description=faker.sentence(),
        edited_by=user.id,
    )


class TestUpdatePostUseCase:
    @pytest.fixture
    def usecase(
        self: Self,
        repository: AbstractPostRepository,
        history_repository: AbstractPostHistoryRepository,
        permissions_repo: AbstractPermissionRepository,
    ) -> UpdatePostUseCase:
        return UpdatePostUseCase(repository, history_repository, permissions_repo)

    async def test_update_post_without_history(
        self: Self,
        usecase: UpdatePostUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
        post: Post,
        update_post_dto: UpdatePostDTO,
    ) -> None:
        repository.get_by_slug.return_value = post
        updated_post = Post(
            **post.model_dump(exclude={"title", "updated_at", "updated_by"}),
            title=update_post_dto.title,
            updated_at=datetime.now(tz=timezone.utc),
            updated_by=update_post_dto.user.id,
        )
        repository.update.return_value = updated_post

        result = await usecase.execute(post.slug, update_post_dto)

        assert result == updated_post
        repository.get_by_slug.assert_awaited_once_with(post.slug)
        repository.update.assert_awaited_once_with(post.id, update_post_dto)
        history_repository.create.assert_not_awaited()

    async def test_update_post_with_history(
        self: Self,
        usecase: UpdatePostUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
        post: Post,
        user: User,
    ) -> None:
        update_dto_with_history = UpdatePostDTO(
            title="New Title",
            user=user,
            save_history=True,
            history_description="Title updated",
        )
        repository.get_by_slug.return_value = post
        updated_post = Post(
            **post.model_dump(exclude={"title", "updated_at", "updated_by"}),
            title="New Title",
            updated_at=datetime.now(tz=timezone.utc),
            updated_by=user.id,
        )
        repository.update.return_value = updated_post

        result = await usecase.execute(post.slug, update_dto_with_history)

        assert result == updated_post
        repository.get_by_slug.assert_awaited_once_with(post.slug)
        repository.update.assert_awaited_once_with(post.id, update_dto_with_history)
        history_repository.create.assert_awaited_once_with(
            post_id=post.id,
            description="Title updated",
            edited_by=UUID(user.id),
        )

    async def test_update_post_not_found(
        self: Self,
        usecase: UpdatePostUseCase,
        repository: AsyncMock,
        update_post_dto: UpdatePostDTO,
    ) -> None:
        repository.get_by_slug.side_effect = PostNotFoundError

        with pytest.raises(PostNotFoundError):
            await usecase.execute("non-existent-slug", update_post_dto)

        repository.get_by_slug.assert_awaited_once_with("non-existent-slug")
        repository.update.assert_not_awaited()

    async def test_update_post_with_history_but_no_description(
        self: Self,
        usecase: UpdatePostUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
        post: Post,
        user: User,
    ) -> None:
        update_dto = UpdatePostDTO(
            title="New Title",
            user=user,
            save_history=True,
            history_description=None,
        )
        repository.get_by_slug.return_value = post
        updated_post = Post(
            **post.model_dump(exclude={"title", "updated_at", "updated_by"}),
            title="New Title",
            updated_at=datetime.now(tz=timezone.utc),
            updated_by=user.id,
        )
        repository.update.return_value = updated_post

        result = await usecase.execute(post.slug, update_dto)

        assert result == updated_post
        history_repository.create.assert_not_awaited()


class TestGetPostHistoryUseCase:
    @pytest.fixture
    def usecase(
        self: Self,
        repository: AbstractPostRepository,
        history_repository: AbstractPostHistoryRepository,
    ) -> GetPostHistoryUseCase:
        return GetPostHistoryUseCase(repository, history_repository)

    async def test_get_post_history(
        self: Self,
        usecase: GetPostHistoryUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
        post: Post,
        post_edit_history: PostEditHistory,
    ) -> None:
        repository.get_by_slug.return_value = post
        history_repository.get_by_post_id.return_value = [post_edit_history]

        result = await usecase.execute(post.slug)

        assert result == [post_edit_history]
        repository.get_by_slug.assert_awaited_once_with(post.slug)
        history_repository.get_by_post_id.assert_awaited_once_with(post.id)

    async def test_get_post_history_empty(
        self: Self,
        usecase: GetPostHistoryUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
        post: Post,
    ) -> None:
        repository.get_by_slug.return_value = post
        history_repository.get_by_post_id.return_value = []

        result = await usecase.execute(post.slug)

        assert result == []
        repository.get_by_slug.assert_awaited_once_with(post.slug)
        history_repository.get_by_post_id.assert_awaited_once_with(post.id)

    async def test_get_post_history_post_not_found(
        self: Self,
        usecase: GetPostHistoryUseCase,
        repository: AsyncMock,
        history_repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.side_effect = PostNotFoundError

        with pytest.raises(PostNotFoundError):
            await usecase.execute("non-existent-slug")

        repository.get_by_slug.assert_awaited_once_with("non-existent-slug")
        history_repository.get_by_post_id.assert_not_awaited()
