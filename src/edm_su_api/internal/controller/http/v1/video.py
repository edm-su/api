from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.video import (
    FindVideo,
    create_count_videos_usecase,
    create_create_video_usecase,
    create_delete_video_usecase,
    create_get_all_videos_usecase,
)
from edm_su_api.internal.entity.video import NewVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import VideoError
from edm_su_api.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
)

router = APIRouter(tags=["Videos"])


@router.get(
    "",
    response_model=list[Video],
    summary="Get all videos",
)
async def get_videos(
    response: Response,
    pagination: PaginatorDeps,
    get_all_usecase: Annotated[
        GetAllVideosUseCase,
        Depends(create_get_all_videos_usecase),
    ],
    count_usecase: Annotated[
        GetCountVideosUseCase,
        Depends(create_count_videos_usecase),
    ],
) -> list[Video]:
    db_videos = await get_all_usecase.execute(
        offset=pagination.skip,
        limit=pagination.limit,
    )
    count = await count_usecase.execute()
    response.headers["X-Total-Count"] = str(count)
    return db_videos


@router.get(
    "/{slug}",
    summary="Get video",
)
async def read_video(
    video: FindVideo,
) -> Video:
    return video


@router.delete(
    "/{slug}",
    summary="Remove video",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video(
    usecase: Annotated[
        DeleteVideoUseCase,
        Depends(create_delete_video_usecase),
    ],
    video: FindVideo,
) -> None:
    await usecase.execute(video.id)


@router.post(
    "",
    summary="Add video",
    status_code=status.HTTP_201_CREATED,
)
async def add_video(
    new_video: NewVideoDto,
    usecase: Annotated[
        CreateVideoUseCase,
        Depends(create_create_video_usecase),
    ],
) -> Video:
    try:
        video = await usecase.execute(new_video)
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    return video
