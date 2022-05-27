from fastapi import Depends, HTTPException

from app.db import database
from app.meilisearch import ms_client
from app.repositories.user_video import PostgresUserVideoRepository
from app.repositories.video import (
    MeilisearchVideoRepository,
    PostgresVideoRepository,
)
from app.schemas.video import PgVideo


async def create_pg_video_repository() -> PostgresVideoRepository:
    return PostgresVideoRepository(database)


async def create_ms_video_repository() -> MeilisearchVideoRepository:
    return MeilisearchVideoRepository(ms_client)


async def create_pg_user_video_repository() -> PostgresUserVideoRepository:
    return PostgresUserVideoRepository(database)


async def find_video(
    slug: str,
    pg_video_repository: PostgresVideoRepository = Depends(
        create_pg_video_repository,
    ),
) -> PgVideo:
    db_video = await pg_video_repository.get_by_slug(slug=slug)

    if not db_video:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    return db_video
