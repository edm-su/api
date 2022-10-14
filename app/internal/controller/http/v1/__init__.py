from fastapi import APIRouter

from . import comment, post, upload, video

router = APIRouter()
router.include_router(video.router, prefix="/videos")
router.include_router(comment.router)
router.include_router(post.router, prefix="/posts")
router.include_router(upload.router, prefix="/upload")
