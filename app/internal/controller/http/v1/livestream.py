from collections.abc import Mapping
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.internal.controller.http.v1.dependencies.auth import get_current_admin
from app.internal.controller.http.v1.dependencies.livestream import (
    create_create_live_stream_usecase,
    create_delete_live_stream_usecase,
    create_get_all_live_streams_usecase,
    create_update_live_stream_usecase,
    find_livestream,
)
from app.internal.entity.livestreams import (
    BaseLiveStream,
    CreateLiveStream,
    LiveStream,
)
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
)
from app.internal.usecase.livestream import (
    CreateLiveStreamUseCase,
    DeleteLiveStreamUseCase,
    GetAllLiveStreamsUseCase,
    UpdateLiveStreamUseCase,
)

router = APIRouter(prefix="/livestreams")


@router.post(
    "",
    status_code=201,
    response_model=LiveStream,
    tags=["Прямые трансляции"],
    summary="Добавление прямой трансляции",
)
async def new_stream(
    stream: CreateLiveStream,
    usecase: CreateLiveStreamUseCase = Depends(
        create_create_live_stream_usecase,
    ),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> LiveStream:
    try:
        return await usecase.execute(stream)
    except LiveStreamAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Live stream already exists",
        ) from None


@router.get(
    "",
    response_model=list[LiveStream],
    tags=["Прямые трансляции"],
    summary="Получение списка прямых трансляций",
)
async def get_streams(
    start: date = Query(date.today() - timedelta(days=2)),
    end: date = Query(date.today() + timedelta(days=31)),
    usecase: GetAllLiveStreamsUseCase = Depends(
        create_get_all_live_streams_usecase,
    ),
) -> list[LiveStream | None]:
    return await usecase.execute(start, end)


@router.get(
    "/{id}",
    response_model=LiveStream,
    tags=["Прямые трансляции"],
    summary="Получение прямой трансляции по id",
)
async def get_stream(
    stream: LiveStream = Depends(find_livestream),
) -> LiveStream:
    return stream


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Прямые трансляции"],
    summary="Удаление прямой трансляции по id",
)
async def delete_stream(
    stream: LiveStream = Depends(find_livestream),
    usecase: DeleteLiveStreamUseCase = Depends(
        create_delete_live_stream_usecase,
    ),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> None:
    try:
        await usecase.execute(stream.id)
    except LiveStreamError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.put(
    "/{id}",
    response_model=LiveStream,
    tags=["Прямые трансляции"],
    summary="Обновление прямой трансляции по id",
)
async def update_stream(
    updated_stream: BaseLiveStream,
    stream: LiveStream = Depends(find_livestream),
    usecase: UpdateLiveStreamUseCase = Depends(
        create_update_live_stream_usecase,
    ),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> LiveStream:
    stream = LiveStream(**updated_stream.dict(), id=stream.id)
    try:
        return await usecase.execute(stream)
    except LiveStreamError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Прямая трансляция не найдена",
        ) from None
