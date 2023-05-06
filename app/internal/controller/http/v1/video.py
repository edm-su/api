from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.helpers import Paginator
from app.internal.controller.http.v1.dependencies import auth
from app.internal.controller.http.v1.dependencies.video import (
    create_count_videos_usecase,
    create_create_video_usecase,
    create_delete_video_usecase,
    create_get_all_videos_usecase,
    find_video,
)
from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.exceptions.video import VideoError
from app.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[Video],
    tags=["Видео"],
    summary="Получить список видео",
)
async def get_videos(
    response: Response,
    pagination: Paginator = Depends(Paginator),
    get_all_usecase: GetAllVideosUseCase = Depends(
        create_get_all_videos_usecase,
    ),
    count_usecase: GetCountVideosUseCase = Depends(
        create_count_videos_usecase,
    ),
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
    response_model=Video,
    tags=["Видео"],
    summary="Получить видео",
)
async def read_video(
    video: Video = Depends(find_video),
) -> Video:
    return video


@router.delete(
    "/{slug}",
    tags=["Видео"],
    summary="Удаление видео",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video(
    admin: Mapping = Depends(auth.get_current_admin),  # noqa: ARG001
    video: Video = Depends(find_video),
    usecase: DeleteVideoUseCase = Depends(create_delete_video_usecase),
) -> None:
    try:
        await usecase.execute(video.id)
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e


@router.post(
    "",
    response_model=Video,
    tags=["Видео"],
    summary="Добавить видео",
    status_code=status.HTTP_201_CREATED,
)
async def add_video(
    new_video: NewVideoDto,
    admin: Mapping = Depends(auth.get_current_admin),  # noqa: ARG001
    usecase: CreateVideoUseCase = Depends(create_create_video_usecase),
) -> Video:
    try:
        video = await usecase.execute(new_video)
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e
    return video
