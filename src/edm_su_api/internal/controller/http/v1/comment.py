from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.comment import (
    create_create_comment_usecase,
    create_get_all_comments_usecase,
    create_get_count_comments_usecase,
    create_get_video_comments_usecase,
)
from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.video import FindVideo
from edm_su_api.internal.controller.http.v1.requests.comment import (
    NewCommentRequest,
)
from edm_su_api.internal.entity.comment import Comment, NewCommentDto
from edm_su_api.internal.usecase.comment import (
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
    current_user: CurrentUser,
    usecase: Annotated[
        CreateCommentUseCase,
        Depends(create_create_comment_usecase),
    ],
    video: FindVideo,
) -> Comment:
    comment = NewCommentDto(
        text=text.text,
        user=current_user,
        video=video,
    )
    return await usecase.execute(comment)


@router.get(
    "/videos/{slug}/comments",
    summary="Get comments for video",
)
async def read_comments(
    usecase: Annotated[
        GetVideoCommentsUseCase,
        Depends(create_get_video_comments_usecase),
    ],
    video: FindVideo,
    # paginator: PaginatorDeps, TODO Add pagination
) -> list[Comment]:
    return await usecase.execute(video=video)


@router.get(
    "/comments",
    summary="Get comments",
)
async def comments_list(
    response: Response,
    usecase: Annotated[
        GetAllCommentsUseCase,
        Depends(create_get_all_comments_usecase),
    ],
    pagination: PaginatorDeps,
    count_usecase: Annotated[
        GetCountCommentsUseCase,
        Depends(create_get_count_comments_usecase),
    ],
) -> list[Comment]:
    response.headers["X-Total_Count"] = str(await count_usecase.execute())
    return await usecase.execute(
        limit=pagination.limit,
        offset=pagination.skip,
    )
