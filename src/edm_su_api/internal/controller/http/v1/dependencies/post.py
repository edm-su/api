from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from edm_su_api.internal.controller.http.v1.dependencies.permissions import (
    SpiceDBPermissionsRepo,
)
from edm_su_api.internal.entity.post import Post
from edm_su_api.internal.usecase.exceptions.post import PostNotFoundError
from edm_su_api.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostBySlugUseCase,
    GetPostCountUseCase,
)
from edm_su_api.internal.usecase.repository.post import PostgresPostRepository
from edm_su_api.pkg.postgres import get_session


async def create_pg_repository(
    *,
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
) -> PostgresPostRepository:
    return PostgresPostRepository(session)


PgRepository = Annotated[
    PostgresPostRepository,
    Depends(create_pg_repository),
]


def create_create_post_usecase(
    *,
    repository: PgRepository,
    spicedb_repository: SpiceDBPermissionsRepo,
) -> CreatePostUseCase:
    return CreatePostUseCase(repository, spicedb_repository)


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
    spicedb_repository: SpiceDBPermissionsRepo,
) -> DeletePostUseCase:
    return DeletePostUseCase(repository, spicedb_repository)


async def find_post(
    slug: Annotated[
        str,
        Path,
    ],
    usecase: Annotated[GetPostBySlugUseCase, Depends(create_get_post_by_slug_usecase)],
) -> Post:
    try:
        return await usecase.execute(slug)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


FindPost = Annotated[Post, Depends(find_post)]
