from fastapi import APIRouter, Depends, Response, status

from app.internal.controller.http.v1.dependencies.auth import (
    get_current_admin,
    get_current_user,
)
from app.internal.controller.http.v1.dependencies.comment import (
    create_create_comment_usecase,
    create_get_all_comments_usecase,
    create_get_count_comments_usecase,
    create_get_video_comments_usecase,
)
from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.controller.http.v1.requests.comment import NewCommentRequest
from app.internal.entity.comment import Comment, NewCommentDto
from app.internal.entity.paginator import Paginator
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.internal.usecase.comment import (
    CreateCommentUseCase,
    GetAllCommentsUseCase,
    GetCountCommentsUseCase,
    GetVideoCommentsUseCase,
)

router = APIRouter(tags=["Comments"])


@router.post(
    "/videos/{slug}/comments",
    status_code=status.HTTP_201_CREATED,
    summary="Create comment",
)
async def new_comment(
    text: NewCommentRequest,
    current_user: User = Depends(get_current_user),
    video: Video = Depends(find_video),
    usecase: CreateCommentUseCase = Depends(create_create_comment_usecase),
) -> Comment:
    comment = NewCommentDto(
        text=text.text,
        user=current_user,
        video=video,
    )
    return await usecase.execute(comment)


@router.get(
    "/videos/{video_slug}/comments",
    summary="Get comments for video",
)
async def read_comments(
    video: Video = Depends(find_video),
    # paginator: Paginator = Depends(Paginator), TODO Add pagination
    usecase: GetVideoCommentsUseCase = Depends(
        create_get_video_comments_usecase,
    ),
) -> list[Comment | None]:
    return await usecase.execute(video=video)


@router.get(
    "/comments",
    summary="Get comments",
)
async def comments_list(
    response: Response,
    _: User = Depends(get_current_admin),
    pagination: Paginator = Depends(Paginator),
    usecase: GetAllCommentsUseCase = Depends(
        create_get_all_comments_usecase,
    ),
    count_usecase: GetCountCommentsUseCase = Depends(
        create_get_count_comments_usecase,
    ),
) -> list[Comment]:
    response.headers["X-Total_Count"] = str(await count_usecase.execute())
    return await usecase.execute(
        limit=pagination.limit,
        offset=pagination.skip,
    )
