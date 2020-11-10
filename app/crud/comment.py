from typing import List, Mapping, Optional

from sqlalchemy import desc, func, select

from app.db import comments, database


async def get_comments_for_video(video_id: int) -> List[Mapping]:
    query = comments.select().where(comments.c.video_id == video_id)
    return await database.fetch_all(query=query)


async def create_comment(
        user_id: int,
        video_id: int,
        text: str,
) -> Optional[Mapping]:
    query = comments.insert().returning(comments)
    values = {'user_id': user_id, 'video_id': video_id, 'text': text}
    return await database.fetch_one(query=query, values=values)


async def get_comments(limit: int = 50, skip: int = 0) -> List[Mapping]:
    query = comments.select().order_by(desc(comments.c.published_at))
    query = query.limit(limit).offset(skip)
    return await database.fetch_all(query=query)


async def get_comments_count() -> int:
    query = select([func.count()]).select_from(comments)
    return await database.fetch_val(query=query)
