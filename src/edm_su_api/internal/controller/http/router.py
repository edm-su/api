from fastapi import APIRouter

from edm_su_api.internal.controller.http import v1

api_router = APIRouter()
api_router.include_router(v1.router)
