from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.internal.entity.livestreams import LiveStream
from app.internal.usecase.exceptions.livestream import LiveStreamNotFoundError
from app.internal.usecase.livestream import (
    CreateLiveStreamUseCase,
    DeleteLiveStreamUseCase,
    GetAllLiveStreamsUseCase,
    GetLiveStreamUseCase,
    UpdateLiveStreamUseCase,
)
from app.internal.usecase.repository.livestream import (
    PostgresLiveStreamRepository,
)
from app.pkg.postgres import get_session


async def create_pg_repository(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresLiveStreamRepository:
    return PostgresLiveStreamRepository(session)


PgRepository = Annotated[
    PostgresLiveStreamRepository,
    Depends(create_pg_repository),
]


def create_get_all_live_streams_usecase(
    repository: PgRepository,
) -> GetAllLiveStreamsUseCase:
    return GetAllLiveStreamsUseCase(repository=repository)


def create_get_live_stream_usecase(
    repository: PgRepository,
) -> GetLiveStreamUseCase:
    return GetLiveStreamUseCase(repository=repository)


def create_create_live_stream_usecase(
    repository: PgRepository,
) -> CreateLiveStreamUseCase:
    return CreateLiveStreamUseCase(repository=repository)


def create_delete_live_stream_usecase(
    repository: PgRepository,
) -> DeleteLiveStreamUseCase:
    return DeleteLiveStreamUseCase(repository=repository)


def create_update_live_stream_usecase(
    repository: PgRepository,
) -> UpdateLiveStreamUseCase:
    return UpdateLiveStreamUseCase(repository=repository)


async def find_livestream(
    live_stream_id: Annotated[
        int,
        Path,
    ],
    usecase: Annotated[
        GetLiveStreamUseCase,
        Depends(create_get_live_stream_usecase),
    ],
) -> LiveStream:
    try:
        return await usecase.execute(live_stream_id=live_stream_id)
    except LiveStreamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None


FindLivestream = Annotated[LiveStream, Depends(find_livestream)]
