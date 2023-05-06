from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.helpers import Paginator
from app.internal.controller.http.v1.dependencies.auth import get_current_admin
from app.internal.controller.http.v1.dependencies.post import (
    create_create_post_usecase,
    create_delete_post_usecase,
    create_get_all_posts_usecase,
    create_get_count_posts_usecase,
    find_post,
)
from app.internal.entity.post import CreatePost, NewPostDTO, Post
from app.internal.usecase.exceptions.video import (
    NotFoundError,
    SlugNotUniqueError,
)
from app.internal.usecase.post import (
    CreatePostUseCase,
    DeletePostUseCase,
    GetAllPostsUseCase,
    GetPostCountUseCase,
)

router = APIRouter()


@router.post(
    "/",
    response_model=Post,
    tags=["Посты"],
    summary="Добавление поста",
)
async def new_post(
    post: CreatePost,
    admin: Mapping = Depends(get_current_admin),  # TODO: изменить тип на User
    usecase: CreatePostUseCase = Depends(create_create_post_usecase),
) -> Post:
    post = NewPostDTO(
        **post.dict(),
        user=admin,  # type: ignore[arg-type]
    )
    try:
        return await usecase.execute(post)
    except SlugNotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Пост с таким slug уже существует",
        ) from None


@router.get(
    "/",
    response_model=list[Post],
    tags=["Посты"],
    summary="Получение списка постов",
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
    response_model=Post,
    tags=["Посты"],
    summary="Получить пост",
)
async def get_post(post: Post = Depends(find_post)) -> Post:
    return post


@router.delete(
    "/{slug}",
    tags=["Посты"],
    summary="Удалить пост",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    slug: str,
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
    usecase: DeletePostUseCase = Depends(create_delete_post_usecase),
) -> None:
    try:
        return await usecase.execute(slug)
    except SlugNotUniqueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Пост с таким slug уже существует",
        ) from None
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден",
        ) from None
