from uuid import UUID

from typing_extensions import Self

from edm_su_api.internal.entity.post import (
    NewPostDTO,
    Post,
    PostEditHistory,
    UpdatePostDTO,
)
from edm_su_api.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
    Object,
)
from edm_su_api.internal.usecase.repository.post import (
    AbstractPostHistoryRepository,
    AbstractPostRepository,
)


class BasePostUseCase:
    def __init__(
        self: Self,
        repository: AbstractPostRepository,
        permissions_repo: AbstractPermissionRepository | None = None,
    ) -> None:
        self.repository = repository
        self.permissions_repo = permissions_repo


class CreatePostUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        new_post: NewPostDTO,
    ) -> Post:
        try:
            await self.repository.get_by_slug(new_post.slug)
            raise PostSlugNotUniqueError(slug=new_post.slug)
        except PostNotFoundError:
            post = await self.repository.create(new_post)
            await self._set_permissions(post)
            return post

    async def _set_permissions(self: Self, post: Post) -> None:
        if self.permissions_repo is not None:
            resource = Object("post", post.slug)

            await self.permissions_repo.write(
                resource,
                "writer",
                Object("role", "admin"),
                "member",
            )

            await self.permissions_repo.write(
                resource,
                "reader",
                Object("user", "*"),
            )


class GetPostBySlugUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        slug: str,
    ) -> Post:
        result = await self.repository.get_by_slug(slug)
        if result is None:
            raise PostNotFoundError
        return result


class GetPostCountUseCase(BasePostUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetAllPostsUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Post]:
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
        )


class DeletePostUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        slug: str,
    ) -> None:
        post = await self.repository.get_by_slug(slug)
        await self.repository.delete(post)
        await self._set_permissions(post)

    async def _set_permissions(self: Self, post: Post) -> None:
        if self.permissions_repo is not None:
            resource = Object("post", post.slug)

            await self.permissions_repo.delete(resource, "reader")


class UpdatePostUseCase(BasePostUseCase):
    def __init__(
        self: Self,
        repository: AbstractPostRepository,
        history_repo: AbstractPostHistoryRepository,
        permissions_repo: AbstractPermissionRepository | None = None,
    ) -> None:
        super().__init__(repository, permissions_repo)
        self.history_repo = history_repo

    async def execute(
        self: Self,
        slug: str,
        update_data: UpdatePostDTO,
    ) -> Post:
        post = await self.repository.get_by_slug(slug)

        updated_post = await self.repository.update(
            post.id,
            update_data,
        )

        if update_data.save_history and update_data.history_description:
            await self.history_repo.create(
                post_id=post.id,
                description=update_data.history_description,
                edited_by=UUID(update_data.user.id),
            )

        return updated_post


class GetPostHistoryUseCase(BasePostUseCase):
    def __init__(
        self: Self,
        repository: AbstractPostRepository,
        history_repo: AbstractPostHistoryRepository,
    ) -> None:
        super().__init__(repository)
        self.history_repo = history_repo

    async def execute(
        self: Self,
        slug: str,
    ) -> list[PostEditHistory]:
        post = await self.repository.get_by_slug(slug)
        return await self.history_repo.get_by_post_id(post.id)
