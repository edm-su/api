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
from app.internal.controller.http.v1.requests.livestream import (
    CreateLiveStreamRequest,
)
from app.internal.entity.livestreams import (
    BaseLiveStream,
    CreateLiveStreamDTO,
    LiveStream,
)
from app.internal.entity.user import User
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

router = APIRouter(prefix="/livestreams", tags=["LiveStreams"])


@router.post(
    "",
    status_code=201,
    summary="Create live stream",
)
async def new_stream(
    stream: CreateLiveStreamRequest,
    usecase: CreateLiveStreamUseCase = Depends(
        create_create_live_stream_usecase,
    ),
    _: User = Depends(get_current_admin),
) -> LiveStream:
    livestram = CreateLiveStreamDTO(
        title=stream.title,
        cancelled=stream.cancelled,
        start_time=stream.start_time,
        end_time=stream.end_time,
        image=stream.image,
        genres=stream.genres,
        url=stream.url,
        slug=stream.slug,
    )
    try:
        return await usecase.execute(livestram)
    except LiveStreamAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Live stream already exists",
        ) from None


@router.get(
    "",
    summary="Get live streams",
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
    summary="Get live stream",
)
async def get_stream(
    stream: LiveStream = Depends(find_livestream),
) -> LiveStream:
    return stream


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete live stream",
)
async def delete_stream(
    stream: LiveStream = Depends(find_livestream),
    usecase: DeleteLiveStreamUseCase = Depends(
        create_delete_live_stream_usecase,
    ),
    _: User = Depends(get_current_admin),
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
    summary="Update live stream",
)
async def update_stream(
    updated_stream: BaseLiveStream,
    stream: LiveStream = Depends(find_livestream),
    usecase: UpdateLiveStreamUseCase = Depends(
        create_update_live_stream_usecase,
    ),
    _: User = Depends(get_current_admin),
) -> LiveStream:
    stream = LiveStream(**updated_stream.dict(), id=stream.id)
    try:
        return await usecase.execute(stream)
    except LiveStreamError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None
