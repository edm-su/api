from collections.abc import Mapping
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status

from app.auth import get_current_admin
from app.crud import livestream
from app.schemas import livestreams

router = APIRouter(prefix="/livestreams")


async def find_stream(
    slug: str = Path(...),
    id_: int = Path(..., alias="id", gt=0),
) -> Mapping:
    stream = await livestream.find_one(id_, slug=slug)
    if not stream:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return stream


@router.post(
    "",
    status_code=201,
    response_model=livestreams.LiveStream,
    tags=["Прямые трансляции"],
)
async def new_stream(
    stream: livestreams.CreateLiveStream,
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> Mapping | None:
    db_streams = await livestream.find_one(slug=stream.slug)
    if db_streams:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Такая трансляция уже существует",
        )
    return await livestream.create(stream)


@router.get(
    "",
    response_model=list[livestreams.LiveStream],
    tags=["Прямые трансляции"],
)
async def get_streams(
    start: date = Query(date.today() - timedelta(days=2)),  # noqa: B008
    end: date = Query(date.today() + timedelta(days=31)),  # noqa: B008
) -> list[Mapping]:
    if start + timedelta(days=45) < end:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Период не может превышать 45 дней",
        )
    return await livestream.find(start, end)


@router.get(
    "/{id}:{slug}",
    response_model=livestreams.LiveStream,
    tags=["Прямые трансляции"],
)
async def get_stream(
    stream: Mapping = Depends(find_stream),
) -> None | Mapping:
    return stream


@router.delete(
    "/{id}:{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Прямые трансляции"],
)
async def delete_stream(
    stream: Mapping = Depends(find_stream),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> None:
    await livestream.remove(stream["id"])


@router.put(
    "/{id}:{slug}",
    response_model=livestreams.LiveStream,
    tags=["Прямые трансляции"],
)
async def update_stream(
    updated_stream: livestreams.BaseLiveStream,
    stream: Mapping = Depends(find_stream),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> Mapping | None:
    return await livestream.update(stream["id"], updated_stream)
