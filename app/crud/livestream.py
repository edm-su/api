from datetime import date, timedelta
from typing import Mapping

from sqlalchemy import between

from app.db import database, livestreams
from app.schemas.livestreams import BaseLiveStream


async def create(
    livestream: BaseLiveStream,
) -> None | Mapping:
    query = livestreams.insert(values=livestream.dict()).returning(livestreams)
    return await database.fetch_one(query)


async def find_one(
    id_: int = None,
    title: str = None,
    slug: str = None,
) -> None | Mapping:
    query = livestreams.select()
    if id_:
        query = query.where(livestreams.c.id == id_)
    if title:
        query = query.where(livestreams.c.title == title)
    if slug:
        query = query.where(livestreams.c.slug == slug)
    query = query.limit(1)
    return await database.fetch_one(query)


async def find(
    start: date = date.today() - timedelta(days=2),
    end: date = date.today() + timedelta(days=31),
    slug: str = None,
) -> list[Mapping]:
    query = livestreams.select()
    query = query.where(between(livestreams.c.start_time, start, end))
    query = query.order_by(livestreams.c.start_time)
    return await database.fetch_all(query)


async def remove(id_: int) -> bool:
    query = livestreams.delete().where(livestreams.c.id == id_)
    return bool(await database.execute(query))


async def update(id_: int, livestream: BaseLiveStream) -> None | Mapping:
    query = livestreams.update().where(livestreams.c.id == id_)
    query = query.returning(livestreams)
    return await database.fetch_one(
        query,
        livestream.dict(
            exclude={"slug"},
            exclude_unset=True,
        ),
    )
