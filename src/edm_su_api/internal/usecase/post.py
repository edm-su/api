from typing_extensions import Self

from edm_su_api.internal.entity.post import NewPostDTO, Post
from edm_su_api.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from edm_su_api.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
    Object,
)
from edm_su_api.internal.usecase.repository.post import AbstractPostRepository


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
