from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from edm_su_api.internal.controller.http.v1.dependencies.livestream import (
    FindLivestream,
    create_create_live_stream_usecase,
    create_delete_live_stream_usecase,
    create_get_all_live_streams_usecase,
    create_update_live_stream_usecase,
)
from edm_su_api.internal.controller.http.v1.requests.livestream import (
    CreateLiveStreamRequest,
)
from edm_su_api.internal.entity.livestreams import (
    BaseLiveStream,
    CreateLiveStreamDTO,
    LiveStream,
)
from edm_su_api.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
)
from edm_su_api.internal.usecase.livestream import (
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
    usecase: Annotated[
        CreateLiveStreamUseCase,
        Depends(create_create_live_stream_usecase),
    ],
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
    usecase: Annotated[
        GetAllLiveStreamsUseCase,
        Depends(create_get_all_live_streams_usecase),
    ],
    start: Annotated[
        date,
        Query(
            default_factory=lambda: (
                datetime.now(tz=timezone.utc).date() - timedelta(days=2)
            ),
        ),
    ],
    end: Annotated[
        date,
        Query(
            default_factory=lambda: (
                datetime.now(tz=timezone.utc).date() - timedelta(days=2)
            ),
        ),
    ],
) -> list[LiveStream]:
    return await usecase.execute(start, end)


@router.get(
    "/{id}",
    summary="Get live stream",
)
# ruff: noqa: FAST003 False positive. The argument is used depending on
async def get_stream(
    stream: FindLivestream,
) -> LiveStream:
    return stream


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete live stream",
)
async def delete_stream(
    usecase: Annotated[
        DeleteLiveStreamUseCase,
        Depends(create_delete_live_stream_usecase),
    ],
    stream: FindLivestream,
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
    usecase: Annotated[
        UpdateLiveStreamUseCase,
        Depends(create_update_live_stream_usecase),
    ],
    stream: FindLivestream,
) -> LiveStream:
    stream = LiveStream(**updated_stream.model_dump(), id=stream.id)
    try:
        return await usecase.execute(stream)
    except LiveStreamError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None
