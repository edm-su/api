from datetime import date, timedelta
from typing import Mapping

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.auth import get_current_admin
from app.internal.controller.http.v1.depencies.livestream import (
    create_create_live_stream_usecase,
    create_delete_live_stream_usecase,
    create_get_all_live_streams_usecase,
    create_update_live_stream_usecase,
    find_live_stream,
)
from app.internal.entity.livestreams import (
    BaseLiveStream,
    CreateLiveStream,
    LiveStream,
)
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsException,
    LiveStreamNotFoundException,
)
from app.internal.usecase.livestream import (
    CreateLiveStreamUseCase,
    DeleteLiveStreamUseCase,
    GetAllLiveStreamsUseCase,
    UpdateLiveStreamUseCase,
)

router = APIRouter(prefix="/livestreams")


@router.post(
    "/",
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
    admin: Mapping = Depends(get_current_admin),
) -> LiveStream:
    try:
        return await usecase.execute(stream)
    except LiveStreamAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Прямая трансляция с таким slug уже существует",
        )


@router.get(
    "/",
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
    if start + timedelta(days=45) < end:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Период не может превышать 45 дней",
        )
    return await usecase.execute(start, end)


@router.get(
    "/{id}",
    response_model=LiveStream,
    tags=["Прямые трансляции"],
    summary="Получение прямой трансляции по id",
)
async def get_stream(
    stream: LiveStream = Depends(find_live_stream),
) -> LiveStream:
    return stream


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Прямые трансляции"],
    summary="Удаление прямой трансляции по id",
)
async def delete_stream(
    stream: LiveStream = Depends(find_live_stream),
    usecase: DeleteLiveStreamUseCase = Depends(
        create_delete_live_stream_usecase,
    ),
    admin: Mapping = Depends(get_current_admin),
) -> None:
    try:
        await usecase.execute(stream.id)
    except LiveStreamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Прямая трансляция не найдена",
        )


@router.put(
    "/{id}",
    response_model=LiveStream,
    tags=["Прямые трансляции"],
    summary="Обновление прямой трансляции по id",
)
async def update_stream(
    updated_stream: BaseLiveStream,
    stream: LiveStream = Depends(find_live_stream),
    usecase: UpdateLiveStreamUseCase = Depends(
        create_update_live_stream_usecase,
    ),
    admin: Mapping = Depends(get_current_admin),
) -> LiveStream:
    stream = LiveStream(**updated_stream.dict(), id=stream.id)
    try:
        return await usecase.execute(stream)
    except LiveStreamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Прямая трансляция не найдена",
        )
