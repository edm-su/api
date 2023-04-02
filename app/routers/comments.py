from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth import get_current_admin, get_current_user
from app.crud import comment, video
from app.helpers import Paginator
from app.schemas.comment import Comment, CommentBase

router = APIRouter()


async def find_video(video_slug: str) -> Mapping:
    db_video = await video.get_video_by_slug(slug=video_slug)
    if not db_video:
        raise HTTPException(status_code=404, detail="Видео не найдено")
    return db_video


@router.post(
    "/videos/{video_slug}/comments",
    response_model=Comment,
    tags=["Комментарии", "Видео"],
    summary="Оставить комментарий",
)
async def new_comment(
    text: CommentBase,
    db_video: dict = Depends(find_video),
    current_user: dict = Depends(get_current_user),
) -> Mapping | None:
    return await comment.create_comment(
        user_id=current_user["id"],
        video_id=db_video["id"],
        text=text.text,
    )


@router.get(
    "/videos/{video_slug}/comments",
    response_model=list[Comment],
    tags=["Комментарии", "Видео"],
    summary="Получить комментарии к видео",
)
async def read_comments(
    db_video: Mapping = Depends(find_video),
) -> list[Mapping]:
    return await comment.get_comments_for_video(video_id=db_video["id"])


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
