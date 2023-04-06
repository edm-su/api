from typing import Self

from app.helpers import Paginator
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)
from app.internal.usecase.repository.user_videos import (
    AbstractUserVideosRepository,
)


class BaseUserVideosUseCase():
    def __init__(
      self: Self,
      repository: AbstractUserVideosRepository,
    ) -> None:
        self.repository = repository


class GetUserVideosUseCase(BaseUserVideosUseCase):
    async def execute(
        self: Self,
        user: User,
        *,
        limit: int = 20,
        skip: int = 0,
    ) -> list[Video]:
        return await self.repository.get_user_videos(
            user,
            limit=limit,
            offset=skip,
        )


class LikeVideoUseCase(BaseUserVideosUseCase):
    async def execute(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        if await self.repository.is_liked(user, video):
            raise UserVideoAlreadyLikedError
        return await self.repository.like_video(user, video)


class UnlikeVideoUseCase(BaseUserVideosUseCase):
    async def execute(
        self: Self,
        user: User,
        video: Video,
    ) -> None:
        if not await self.repository.is_liked(user, video):
            raise UserVideoNotLikedError
        return await self.repository.unlike_video(user, video)
