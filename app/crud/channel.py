from typing import List, Mapping

from sqlalchemy import func, select

from app.db import channels, database


async def get_channel_by_slug(slug: str) -> Mapping:
    query = channels.select().where(channels.c.slug == slug)
    return await database.fetch_one(query=query)


async def get_channels(skip: int = 0, limit: int = 25) -> List[Mapping]:
    query = channels.select().offset(skip).limit(limit)
    return await database.fetch_all(query=query)


async def get_channels_count() -> int:
    query = select([func.count()]).select_from(channels)
    return await database.fetch_val(query=query)
