from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from starlette import status

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    OptionalUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.video import (
    FindVideo,
    create_count_videos_usecase,
    create_create_video_usecase,
    create_delete_video_usecase,
    create_get_all_videos_usecase,
    create_get_video_by_slug_usecase,
    create_update_video_usecase,
)
from edm_su_api.internal.controller.http.v1.requests.video import UpdateVideoRequest
from edm_su_api.internal.entity.video import NewVideoDto, UpdateVideoDto, Video
from edm_su_api.internal.usecase.exceptions.video import VideoError, VideoNotFoundError
from edm_su_api.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    UpdateVideoUseCase,
)

router = APIRouter(tags=["Videos"])


@router.get(
    "",
    summary="Get all videos",
)
async def get_videos(
    response: Response,
    pagination: PaginatorDeps,
    user: OptionalUser,
    get_all_usecase: Annotated[
        GetAllVideosUseCase,
        Depends(create_get_all_videos_usecase),
    ],
    count_usecase: Annotated[
        GetCountVideosUseCase,
        Depends(create_count_videos_usecase),
    ],
) -> list[Video]:
    user_id = None
    if user:
        user_id = user.id
    db_videos = await get_all_usecase.execute(
        offset=pagination.skip,
        limit=pagination.limit,
        user_id=user_id,
    )
    count = await count_usecase.execute()
    response.headers["X-Total-Count"] = str(count)
    return db_videos


@router.get(
    "/{slug}",
    summary="Get video",
)
async def read_video(
    user: OptionalUser,
    slug: Annotated[
        str,
        Path,
    ],
    usecase: Annotated[
        GetVideoBySlugUseCase,
        Depends(create_get_video_by_slug_usecase),
    ],
) -> Video:
    user_id = None
    if user:
        user_id = user.id
    try:
        return await usecase.execute(slug, user_id)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


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


@router.patch(
    "/{slug}",
    summary="Edit video",
    status_code=status.HTTP_200_OK,
)
async def update_video(
    update_data: UpdateVideoRequest,
    usecase: Annotated[
        UpdateVideoUseCase,
        Depends(create_update_video_usecase),
    ],
    slug: Annotated[str, Path()],
) -> Video:
    update_dto = UpdateVideoDto(
        slug=slug,
        **update_data.model_dump(exclude={"slug"}, exclude_unset=True),
    )
    try:
        return await usecase.execute(update_dto)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
