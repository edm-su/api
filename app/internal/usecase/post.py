from abc import ABC

from app.helpers import Paginator
from app.internal.entity.post import NewPostDTO, Post
from app.internal.usecase.exceptions.video import (
    NotDeletedException,
    NotFoundException,
    SlugNotUniqueException,
)
from app.internal.usecase.repository.post import AbstractPostRepository


class BasePostUseCase(ABC):
    def __init__(self, repository: AbstractPostRepository) -> None:
        self.repository = repository


class CreatePostUseCase(BasePostUseCase):
    async def execute(self, new_post: NewPostDTO) -> Post:
        if await self.repository.get_by_slug(new_post.slug):
            raise SlugNotUniqueException(slug=new_post.slug, entity="post")
        return await self.repository.create(new_post)


class GetPostBySlugUseCase(BasePostUseCase):
    async def execute(self, slug: str) -> Post:
        result = await self.repository.get_by_slug(slug)
        if result is None:
            raise NotFoundException(entity="post")
        return result


class GetPostCountUseCase(BasePostUseCase):
    async def execute(self) -> int:
        return await self.repository.count()


class GetAllPostsUseCase(BasePostUseCase):
    async def execute(
        self,
        paginator: Paginator = Paginator(),
    ) -> list[Post | None]:
        return await self.repository.get_all(paginator=paginator)


class DeletePostUseCase(BasePostUseCase):
    async def execute(self, slug: str) -> None:
        post = await self.repository.get_by_slug(slug)
        if post is None:
            raise NotFoundException(entity="post")
        if not await self.repository.delete(post):
            raise NotDeletedException(entity="post")
        return None
