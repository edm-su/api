from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.post import (
    FindPost,
    create_create_post_usecase,
    create_delete_post_usecase,
    create_get_all_posts_usecase,
    create_get_count_posts_usecase,
    create_get_post_history_usecase,
    create_update_post_usecase,
)
from edm_su_api.internal.controller.http.v1.requests.post import UpdatePostRequest
from edm_su_api.internal.entity.post import (
    NewPost,
    NewPostDTO,
    Post,
    PostEditHistory,
    UpdatePostDTO,
)
from edm_su_api.internal.usecase.exceptions.post import (
    PostError,
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from edm_su_api.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostCountUseCase,
    GetPostHistoryUseCase,
    UpdatePostUseCase,
)

router = APIRouter(tags=["Posts"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create post",
)
async def new_post(
    post: NewPost,
    user: CurrentUser,
    usecase: Annotated[
        CreatePostUseCase,
        Depends(create_create_post_usecase),
    ],
) -> Post:
    new_post = NewPostDTO(
        title=post.title,
        annotation=post.annotation,
        text=post.text,
        slug=post.slug,
        published_at=post.published_at,  # type: ignore[assigned]
        thumbnail=post.thumbnail,
        user=user,
    )
    try:
        return await usecase.execute(new_post)
    except PostSlugNotUniqueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None


@router.get(
    "",
    summary="Get all posts",
)
async def get_posts(
    response: Response,
    paginate: PaginatorDeps,
    usecase: Annotated[
        GetAllPostsUseCase,
        Depends(create_get_all_posts_usecase),
    ],
    count_usecase: Annotated[
        GetPostCountUseCase,
        Depends(create_get_count_posts_usecase),
    ],
) -> list[Post]:
    response.headers["X-Total-Count"] = str(await count_usecase.execute())
    return await usecase.execute(
        paginate.skip,
        paginate.limit,
    )


@router.get(
    "/{slug}",
    summary="Get post",
)
# ruff: noqa: FAST003 False positive. The argument is used depending on
async def get_post(post: FindPost) -> Post:
    return post


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post",
)
async def delete_post(
    slug: str,
    usecase: Annotated[
        DeletePostUseCase,
        Depends(create_delete_post_usecase),
    ],
) -> None:
    try:
        await usecase.execute(slug)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None
    except PostError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from None


@router.put(
    "/{slug}",
    summary="Update post",
)
async def update_post(
    slug: str,
    request: UpdatePostRequest,
    user: CurrentUser,
    usecase: Annotated[
        UpdatePostUseCase,
        Depends(create_update_post_usecase),
    ],
) -> Post:
    update_data = UpdatePostDTO(
        title=request.title,
        annotation=request.annotation,
        text=request.text,
        thumbnail=request.thumbnail,
        published_at=request.published_at,
        user=user,
        save_history=request.save_history,
        history_description=request.history_description,
    )

    try:
        return await usecase.execute(slug, update_data)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None


@router.get(
    "/{slug}/history",
    summary="Get post edit history",
)
async def get_post_history(
    slug: str,
    usecase: Annotated[
        GetPostHistoryUseCase,
        Depends(create_get_post_history_usecase),
    ],
) -> list[PostEditHistory]:
    try:
        return await usecase.execute(slug)
    except PostNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None
