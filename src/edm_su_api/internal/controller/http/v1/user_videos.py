from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.user_videos import (
    create_get_user_videos_usecase,
    create_like_video_usecase,
    create_unlike_video_usecase,
)
from edm_su_api.internal.controller.http.v1.dependencies.video import FindVideo
from edm_su_api.internal.entity.video import Video
from edm_su_api.internal.usecase.exceptions.user_videos import (
    UserVideoAlreadyLikedError,
    UserVideoNotLikedError,
)
from edm_su_api.internal.usecase.user_videos import (
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
    user: CurrentUser,
    usecase: Annotated[
        LikeVideoUseCase,
        Depends(create_like_video_usecase),
    ],
    video: FindVideo,
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
    user: CurrentUser,
    usecase: Annotated[
        UnlikeVideoUseCase,
        Depends(create_unlike_video_usecase),
    ],
    video: FindVideo,
) -> None:
    try:
        await usecase.execute(user, video)
    except UserVideoNotLikedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.get(
    "/user/videos",
    summary="Get user videos",
)
async def get_user_videos(
    pagination: PaginatorDeps,
    usecase: Annotated[
        GetUserVideosUseCase,
        Depends(create_get_user_videos_usecase),
    ],
    user: CurrentUser,
) -> list[Video]:
    return await usecase.execute(
        user,
        limit=pagination.limit,
        skip=pagination.skip,
    )
