from typing_extensions import Self

from app.helpers import Paginator
from app.internal.entity.post import NewPostDTO, Post
from app.internal.usecase.exceptions.post import (
    PostNotDeletedError,
    PostNotFoundError,
)
from app.internal.usecase.exceptions.video import (
    NotFoundError,
    SlugNotUniqueError,
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
            raise SlugNotUniqueError(slug=new_post.slug, entity="post")
        return await self.repository.create(new_post)


class GetPostBySlugUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        slug: str,
    ) -> Post:
        result = await self.repository.get_by_slug(slug)
        if result is None:
            raise NotFoundError(entity="post")
        return result


class GetPostCountUseCase(BasePostUseCase):
    async def execute(self: Self) -> int:
        return await self.repository.count()


class GetAllPostsUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        paginator: Paginator,
    ) -> list[Post | None]:
        return await self.repository.get_all(
            skip=paginator.skip,
            limit=paginator.limit,
        )


class DeletePostUseCase(BasePostUseCase):
    async def execute(
        self: Self,
        slug: str,
    ) -> None:
        post = await self.repository.get_by_slug(slug)
        if post is None:
            raise PostNotFoundError
        if not await self.repository.delete(post):
            raise PostNotDeletedError
