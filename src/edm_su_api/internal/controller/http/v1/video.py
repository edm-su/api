from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from starlette import status

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    OptionalUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.paginator import (
    PaginatorDeps,
)
from edm_su_api.internal.controller.http.v1.dependencies.video import (
    FindVideoIncludingDeleted,
    create_count_videos_usecase,
    create_create_video_usecase,
    create_delete_video_usecase,
    create_get_all_videos_usecase,
    create_get_video_by_slug_usecase,
    create_restore_video_usecase,
    create_update_video_usecase,
)
from edm_su_api.internal.controller.http.v1.requests.video import UpdateVideoRequest
from edm_su_api.internal.entity.video import (
    DeleteType,
    NewVideoDto,
    UpdateVideoDto,
    Video,
)
from edm_su_api.internal.usecase.exceptions.video import (
    VideoAlreadyDeletedError,
    VideoError,
    VideoNotDeletedError,
    VideoNotFoundError,
    VideoRestoreError,
)
from edm_su_api.internal.usecase.video import (
    CreateVideoUseCase,
    DeleteVideoUseCase,
    GetAllVideosUseCase,
    GetCountVideosUseCase,
    GetVideoBySlugUseCase,
    RestoreVideoUseCase,
    UpdateVideoUseCase,
)

router = APIRouter(
    tags=["Videos"],
    responses={
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        }
    },
)


@router.get(
    "",
    summary="Get all videos",
    description="""
    Retrieve a paginated list of videos.

    By default, only active (non-deleted) videos are returned. Use the
    `include_deleted` parameter to include soft-deleted videos in the response.

    **Response includes deletion status:**
    - `deleted`: Boolean indicating if the video is soft-deleted
    - `delete_type`: Type of deletion (temporary/permanent) if video is deleted

    **Headers:**
    - `X-Total-Count`: Total number of videos (excluding deleted unless
      include_deleted=true)
    """,
    responses={
        200: {
            "description": "List of videos with deletion status",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "title": "Active Video",
                            "slug": "active-video",
                            "deleted": False,
                            "delete_type": None,
                            "date": "2024-01-01",
                            "yt_id": "abc123",
                            "yt_thumbnail": "https://example.com/thumb.jpg",
                            "duration": 180,
                            "is_favorite": False,
                            "is_blocked_in_russia": False,
                        },
                        {
                            "id": 2,
                            "title": "Deleted Video",
                            "slug": "deleted-video",
                            "deleted": True,
                            "delete_type": "temporary",
                            "date": "2024-01-02",
                            "yt_id": "def456",
                            "yt_thumbnail": "https://example.com/thumb2.jpg",
                            "duration": 240,
                            "is_favorite": True,
                            "is_blocked_in_russia": False,
                        },
                    ]
                }
            },
        }
    },
)
async def get_videos(  # noqa: PLR0913
    response: Response,
    pagination: PaginatorDeps,
    user: OptionalUser,
    get_all_usecase: Annotated[
        GetAllVideosUseCase,
        Depends(create_get_all_videos_usecase),
    ],
    count_usecase: Annotated[
        GetCountVideosUseCase,
        Depends(create_count_videos_usecase),
    ],
    *,
    include_deleted: Annotated[
        bool,
        Query(
            description=(
                "Include soft-deleted videos in the response. When true, both "
                "active and soft-deleted videos are returned with deletion "
                "status indicators."
            ),
            examples=False,
        ),
    ] = False,
) -> list[Video]:
    user_id = None
    if user:
        user_id = user.id
    db_videos = await get_all_usecase.execute(
        offset=pagination.skip,
        limit=pagination.limit,
        user_id=user_id,
        include_deleted=include_deleted,
    )
    count = await count_usecase.execute()
    response.headers["X-Total-Count"] = str(count)
    return db_videos


@router.get(
    "/{slug}",
    summary="Get video by slug",
    description="""
    Retrieve a specific video by its slug identifier.

    This endpoint returns both active and soft-deleted videos. The response includes
    deletion status fields to indicate if the video has been soft-deleted.

    **Response includes deletion status:**
    - `deleted`: Boolean indicating if the video is soft-deleted
    - `delete_type`: Type of deletion (temporary/permanent) if video is deleted
    """,
    responses={
        200: {
            "description": "Video details with deletion status",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Sample Video",
                        "slug": "sample-video",
                        "deleted": False,
                        "delete_type": None,
                        "date": "2024-01-01",
                        "yt_id": "abc123",
                        "yt_thumbnail": "https://example.com/thumb.jpg",
                        "duration": 180,
                        "is_favorite": False,
                        "is_blocked_in_russia": False,
                    }
                }
            },
        },
        404: {
            "description": "Video not found",
            "content": {"application/json": {"example": {"detail": "Video not found"}}},
        },
    },
)
async def read_video(
    user: OptionalUser,
    slug: Annotated[
        str,
        Path(description="Unique slug identifier for the video"),
    ],
    usecase: Annotated[
        GetVideoBySlugUseCase,
        Depends(create_get_video_by_slug_usecase),
    ],
) -> Video:
    user_id = None
    if user:
        user_id = user.id
    try:
        return await usecase.execute(slug, user_id)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete(
    "/{slug}",
    summary="Delete video",
    status_code=status.HTTP_204_NO_CONTENT,
    description="""
    Delete a video with support for both soft and permanent deletion.

    **Deletion Types:**
    - `temporary=true` (default): Soft-delete the video (can be restored later)
    - `temporary=false`: Permanently delete the video (cannot be restored)

    **Behavior for already soft-deleted videos:**
    - `temporary=true`: Returns 409 Conflict (video already deleted)
    - `temporary=false`: Permanently deletes the soft-deleted video
    """,
    responses={
        204: {"description": "Video successfully deleted"},
        404: {
            "description": "Video not found",
            "content": {"application/json": {"example": {"detail": "Video not found"}}},
        },
        409: {
            "description": (
                "Video already deleted (when attempting temporary deletion of "
                "already soft-deleted video)"
            ),
            "content": {
                "application/json": {"example": {"detail": "Video is already deleted"}}
            },
        },
        400: {
            "description": "Bad request - general video operation error",
            "content": {
                "application/json": {"example": {"detail": "Invalid video operation"}}
            },
        },
    },
)
async def delete_video(
    usecase: Annotated[
        DeleteVideoUseCase,
        Depends(create_delete_video_usecase),
    ],
    video: FindVideoIncludingDeleted,
    *,
    temporary: Annotated[
        bool,
        Query(
            description=(
                "Whether to perform temporary (soft) deletion (true) or "
                "permanent deletion (false). Soft-deleted videos can be "
                "restored, permanently deleted videos cannot."
            ),
            examples=True,
        ),
    ] = True,
) -> None:
    delete_type = DeleteType.TEMPORARY
    if not temporary:
        delete_type = DeleteType.PERMANENT

    try:
        await usecase.execute(video.id, type_=delete_type)
    except VideoAlreadyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "",
    summary="Create new video",
    status_code=status.HTTP_201_CREATED,
    description="""
    Create a new video entry in the system.

    The created video will have `deleted=false` and `delete_type=null` by default.
    """,
    responses={
        201: {
            "description": "Video successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "New Video",
                        "slug": "new-video",
                        "deleted": False,
                        "delete_type": None,
                        "date": "2024-01-01",
                        "yt_id": "abc123",
                        "yt_thumbnail": "https://example.com/thumb.jpg",
                        "duration": 180,
                        "is_favorite": False,
                        "is_blocked_in_russia": False,
                    }
                }
            },
        },
        409: {
            "description": "Conflict - video with same YouTube ID already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Video with yt_id abc123 already exists"}
                }
            },
        },
    },
)
async def add_video(
    new_video: NewVideoDto,
    usecase: Annotated[
        CreateVideoUseCase,
        Depends(create_create_video_usecase),
    ],
) -> Video:
    try:
        video = await usecase.execute(new_video)
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    return video


@router.patch(
    "/{slug}",
    summary="Update video",
    status_code=status.HTTP_200_OK,
    description="""
    Update an existing video's properties.

    This endpoint can update both active and soft-deleted videos. The response
    includes the current deletion status of the video.
    """,
    responses={
        200: {
            "description": "Video successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Updated Video",
                        "slug": "updated-video",
                        "deleted": False,
                        "delete_type": None,
                        "date": "2024-01-01",
                        "yt_id": "abc123",
                        "yt_thumbnail": "https://example.com/thumb.jpg",
                        "duration": 180,
                        "is_favorite": True,
                        "is_blocked_in_russia": False,
                    }
                }
            },
        },
        404: {
            "description": "Video not found",
            "content": {"application/json": {"example": {"detail": "Video not found"}}},
        },
        409: {
            "description": "Conflict - invalid update operation",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid video update operation"}
                }
            },
        },
    },
)
async def update_video(
    update_data: UpdateVideoRequest,
    usecase: Annotated[
        UpdateVideoUseCase,
        Depends(create_update_video_usecase),
    ],
    slug: Annotated[
        str, Path(description="Unique slug identifier for the video to update")
    ],
) -> Video:
    update_dto = UpdateVideoDto(
        slug=slug,
        **update_data.model_dump(exclude={"slug"}, exclude_unset=True),
    )
    try:
        return await usecase.execute(update_dto)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e


@router.post(
    "/{slug}/restore",
    summary="Restore soft-deleted video",
    status_code=status.HTTP_200_OK,
    description="""
    Restore a soft-deleted video to active status.

    **Requirements:**
    - Video must be soft-deleted (deleted=true, delete_type=temporary)
    - Only administrators can restore videos

    **This operation:**
    - Sets `deleted=false` and `delete_type=null`
    - Re-adds the video to the search index
    - Restores full video functionality
    - Logs the restoration action with timestamp and user information
    """,
    responses={
        200: {
            "description": "Video successfully restored",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Restored Video",
                        "slug": "restored-video",
                        "deleted": False,
                        "delete_type": None,
                        "date": "2024-01-01",
                        "yt_id": "abc123",
                        "yt_thumbnail": "https://example.com/thumb.jpg",
                        "duration": 180,
                        "is_favorite": False,
                        "is_blocked_in_russia": False,
                    }
                }
            },
        },
        404: {
            "description": "Video not found",
            "content": {"application/json": {"example": {"detail": "Video not found"}}},
        },
        409: {
            "description": "Video is not deleted (cannot restore active video)",
            "content": {
                "application/json": {"example": {"detail": "Video is not deleted"}}
            },
        },
        400: {
            "description": "Bad request - restore operation failed",
            "content": {
                "application/json": {
                    "examples": {
                        "restore_error": {
                            "summary": "General restore error",
                            "value": {"detail": "Failed to restore video"},
                        },
                        "video_error": {
                            "summary": "Video operation error",
                            "value": {"detail": "Invalid video operation"},
                        },
                    }
                }
            },
        },
        403: {
            "description": "Forbidden - insufficient permissions to restore video",
            "content": {
                "application/json": {"example": {"detail": "Insufficient permissions"}}
            },
        },
    },
)
async def restore_video(
    usecase: Annotated[
        RestoreVideoUseCase,
        Depends(create_restore_video_usecase),
    ],
    video: FindVideoIncludingDeleted,
) -> Video:
    try:
        return await usecase.execute(video.id)
    except VideoNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except VideoNotDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except VideoRestoreError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except VideoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
