from datetime import date, timedelta
from typing import Optional, Mapping

from sqlalchemy import between

from app.db import livestreams, database
from app.schemas.livestreams import BaseLiveStream


async def create(
        livestream: BaseLiveStream,
) -> Optional[Mapping]:
    query = livestreams.insert(values=livestream.dict()).returning(livestreams)
    return await database.fetch_one(query)


async def find_one(
        id_: int = None,
        title: str = None,
        slug: str = None,
) -> Optional[Mapping]:
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
) -> list[Mapping]:
    query = livestreams.select()
    query = query.where(between(livestreams.c.start_time, start, end))
    return await database.fetch_all(query)
