from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.internal.controller.http.v1.dependencies.auth import get_current_admin
from app.internal.controller.http.v1.dependencies.post import (
    create_create_post_usecase,
    create_delete_post_usecase,
    create_get_all_posts_usecase,
    create_get_count_posts_usecase,
    find_post,
)
from app.internal.controller.http.v1.requests.post import CreatePostRequest
from app.internal.entity.paginator import Paginator
from app.internal.entity.post import NewPostDTO, Post
from app.internal.entity.user import User
from app.internal.usecase.exceptions.post import (
    PostError,
    PostNotFoundError,
    PostSlugNotUniqueError,
)
from app.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostCountUseCase,
)

router = APIRouter(tags=["Posts"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create post",
)
async def new_post(
    post: CreatePostRequest,
    admin: User = Depends(get_current_admin),
    usecase: CreatePostUseCase = Depends(create_create_post_usecase),
) -> Post:
    new_post = NewPostDTO(
        title=post.title,
        annotation=post.annotation,
        text=post.text,
        slug=post.slug,
        published_at=post.published_at,  # type: ignore[assigned]
        thumbnail=post.thumbnail,
        user=admin,
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
    paginate: Paginator = Depends(Paginator),
    usecase: GetAllPostsUseCase = Depends(create_get_all_posts_usecase),
    count_usecase: GetPostCountUseCase = Depends(
        create_get_count_posts_usecase,
    ),
) -> list[Post | None]:
    response.headers["X-Total-Count"] = str(await count_usecase.execute())
    return await usecase.execute(paginator=paginate)


@router.get(
    "/{slug}",
    summary="Get post",
)
async def get_post(post: Post = Depends(find_post)) -> Post:
    return post


@router.delete(
    "/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post",
)
async def delete_post(
    slug: str,
    _: User = Depends(get_current_admin),
    usecase: DeletePostUseCase = Depends(create_delete_post_usecase),
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
