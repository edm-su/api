from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.entity.post import Post
from app.internal.usecase.exceptions.post import PostNotFoundError
from app.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostBySlugUseCase,
    GetPostCountUseCase,
)
from app.internal.usecase.repository.post import PostgresPostRepository
from app.pkg.postgres import get_session


async def create_pg_repository(
    *,
    db_session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresPostRepository:
    async with db_session.begin() as session:
        return PostgresPostRepository(session)  # type: ignore[arg-type]


PgRepository = Annotated[
    PostgresPostRepository,
    Depends(create_pg_repository),
]


def create_create_post_usecase(
    *,
    repository: PgRepository,
) -> CreatePostUseCase:
    return CreatePostUseCase(repository)


def create_get_all_posts_usecase(
    *,
    repository: PgRepository,
) -> GetAllPostsUseCase:
    return GetAllPostsUseCase(repository)


def create_get_count_posts_usecase(
    *,
    repository: PgRepository,
) -> GetPostCountUseCase:
    return GetPostCountUseCase(repository)


def create_get_post_by_slug_usecase(
    *,
    repository: PgRepository,
) -> GetPostBySlugUseCase:
    return GetPostBySlugUseCase(repository)


def create_delete_post_usecase(
    *,
    repository: PgRepository,
) -> DeletePostUseCase:
    return DeletePostUseCase(repository)


async def find_post(
    slug: Annotated[
        str,
        Path,
    ],
    usecase: GetPostBySlugUseCase = Depends(create_get_post_by_slug_usecase),
) -> Post:
    try:
        return await usecase.execute(slug)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


FindPost = Annotated[Post, Depends(find_post)]
