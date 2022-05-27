from typing import Any

from databases.interfaces import Record
from sqlalchemy import case, exists, select
from sqlalchemy.sql.elements import Label

from app.db import database, liked_videos, videos


def is_liked(user_id: int) -> Label:
    return case(
        [
            (
                exists(
                    select([liked_videos])
                    .where(liked_videos.c.video_id == videos.c.id)
                    .where(liked_videos.c.user_id == user_id),
                ),
                "t",
            ),
        ],
        else_="f",
    ).label("liked")


async def get_related_videos(
    title: str,
    limit: int = 25,
    *,
    deleted: bool = False,
    user_id: int | None = None,
) -> list[Record]:
    selected_tables: list[Any] = [videos]
    if user_id:
        selected_tables.append(is_liked(user_id))

    query = select(selected_tables).where(videos.c.deleted == deleted)
    query = query.order_by(videos.c.title.op("<->")(title))
    query = query.limit(limit).offset(1)
    return await database.fetch_all(query=query)
