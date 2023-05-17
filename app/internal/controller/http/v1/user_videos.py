from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.helpers import Paginator
from app.internal.controller.http.v1.dependencies.auth import get_current_user
from app.internal.controller.http.v1.dependencies.user import (
    create_get_user_by_username_usecase,
)
from app.internal.controller.http.v1.dependencies.user_videos import (
    create_get_user_videos_usecase,
    create_like_video_usecase,
    create_unlike_video_usecase,
)
from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.exceptions.user import UserNotFoundError
from app.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)
from app.internal.usecase.user import GetUserByUsernameUseCase
from app.internal.usecase.user_videos import (
    GetUserVideosUseCase,
    LikeVideoUseCase,
    UnlikeVideoUseCase,
)

router = APIRouter(tags=["Liked Videos"])


@router.post(
    "/videos/{slug}/like",
    summary="Like video",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def like_video(
    video: Video = Depends(find_video),
    usecase: LikeVideoUseCase = Depends(create_like_video_usecase),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await usecase.execute(user, video)
    except UserVideoAlreadyLikedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.delete(
    "/videos/{slug}/like",
    summary="Unlike video",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlike_video(
    video: Video = Depends(find_video),
    usecase: UnlikeVideoUseCase = Depends(create_unlike_video_usecase),
    user: User = Depends(get_current_user),
) -> None:
    try:
        await usecase.execute(user, video)
    except UserVideoNotLikedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.get(
    "/users/{username}/videos",
    summary="Get user videos",
    response_model=list[Video],
)
async def get_user_videos(
    username: str = Path(),
    usecase: GetUserVideosUseCase = Depends(create_get_user_videos_usecase),
    get_user_usecase: GetUserByUsernameUseCase = Depends(
        create_get_user_by_username_usecase,
    ),
    pagination: Paginator = Depends(Paginator),
) -> list[Video]:
    try:
        user = await get_user_usecase.execute(username)
        return await usecase.execute(
            user,
            limit=pagination.limit,
            skip=pagination.skip,
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
