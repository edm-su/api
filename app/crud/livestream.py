from typing import Optional, Mapping

from app.db import livestreams, database
from app.schemas.livestreams import BaseLiveStream


async def create(
        livestream: BaseLiveStream,
) -> Optional[Mapping]:
    query = livestreams.insert(values=livestream.dict()).returning(livestreams)
    return await database.fetch_one(query)


async def find_one(id_: int = None, title: str = None) -> Optional[Mapping]:
    query = livestreams.select()
    if id_:
        query = query.where(livestreams.c.id == id_)
    if title:
        query = query.where(livestreams.c.title == title)
    query = query.limit(1)
    return await database.fetch_one(query)
