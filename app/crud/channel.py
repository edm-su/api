from typing import List

from sqlalchemy import func, select

from app.db import channels, database
from app.schemas.channel import BaseChannel


async def get_channel_by_slug(slug: str) -> dict:
    query = channels.select().where(channels.c.slug == slug)
    return await database.fetch_one(query=query)


async def get_channels(
        skip: int = 0,
        limit: int = 25,
        ids: List[int] = None,
) -> List[dict]:
    query = channels.select().offset(skip).limit(limit)
    if ids:
        query = query.where(channels.c.id.in_(ids))
    return await database.fetch_all(query=query)


async def get_channels_count() -> int:
    query = select([func.count()]).select_from(channels)
    return await database.fetch_val(query=query)


async def create_channel(channel: BaseChannel) -> dict:
    query = channels.insert().returning(channels)
    return await database.fetch_one(query, channel.dict())


async def delete_channel(id_: int) -> bool:
    query = channels.delete()
    query = query.where(channels.c.id == id_).returning(channels)
    return bool(await database.fetch_one(query))
