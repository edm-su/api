from collections.abc import Mapping

from fastapi import (
    APIRouter,
    Depends,
    Response,
)

from app.auth import (
    get_current_admin,
    get_current_user,
)
from app.crud import comment
from app.helpers import Paginator
from app.internal.controller.http.v1.depencies.video import find_video
from app.internal.entity.video import Video
from app.schemas.comment import (
    Comment,
    CommentBase,
)

router = APIRouter()


@router.post(
    "/videos/{video_slug}/comments",
    response_model=Comment,
    tags=["Комментарии", "Видео"],
    summary="Оставить комментарий",
)
async def new_comment(
    text: CommentBase,
    video: Video = Depends(find_video),
    current_user: dict = Depends(get_current_user),
) -> Mapping | None:
    return await comment.create_comment(
        user_id=current_user["id"],
        video_id=video.id,
        text=text.text,
    )


@router.get(
    "/videos/{video_slug}/comments",
    response_model=list[Comment],
    tags=["Комментарии", "Видео"],
    summary="Получить комментарии к видео",
)
async def read_comments(
    video: Video = Depends(find_video),
) -> list[Mapping]:
    return await comment.get_comments_for_video(video_id=video.id)


@router.get(
    "/comments",
    response_model=list[Comment],
    tags=["Комментарии"],
    summary="Получить список комментариев ко всем видео",
)
async def comments_list(
    response: Response,
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
    pagination: Paginator = Depends(Paginator),
) -> list[Mapping]:
    response.headers["X-Total_Count"] = str(await comment.get_comments_count())
    return await comment.get_comments(
        limit=pagination.limit,
        skip=pagination.skip,
    )
