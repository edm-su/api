from typing_extensions import Self

from app.internal.entity.post import NewPostDTO, Post
from app.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from app.internal.usecase.repository.post import AbstractPostRepository


class BasePostUseCase:
    def __init__(
        self: Self,
        repository: AbstractPostRepository,
    ) -> None:
        self.repository = repository


class CreatePostUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        new_post: NewPostDTO,
    ) -> Post:
        if await self.repository.get_by_slug(new_post.slug):
            raise PostSlugNotUniqueError(slug=new_post.slug)
        return await self.repository.create(new_post)


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
