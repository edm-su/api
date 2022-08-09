from fastapi import APIRouter

from . import video

router = APIRouter()
router.include_router(video.router, prefix="/videos", tags=["videos"])
