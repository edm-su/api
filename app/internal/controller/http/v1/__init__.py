from fastapi import APIRouter

from . import comment, video

router = APIRouter()
router.include_router(video.router, prefix="/videos")
router.include_router(comment.router, prefix="/comments")
