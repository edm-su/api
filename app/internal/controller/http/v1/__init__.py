from fastapi import APIRouter

from . import (
    comment,
    livestream,
    post,
    upload,
    user_videos,
    video,
)

router = APIRouter()
router.include_router(video.router, prefix="/videos")
router.include_router(comment.router)
router.include_router(user_videos.router)
router.include_router(post.router, prefix="/posts")
router.include_router(upload.router, prefix="/upload")
router.include_router(livestream.router)
