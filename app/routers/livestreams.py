from typing import Mapping, Optional

from fastapi import APIRouter, Depends

from app.auth import get_current_admin
from app.crud import livestream
from app.schemas import livestreams

router = APIRouter(prefix='/livestreams')


@router.post('/', status_code=201)
async def new_stream(
        stream: livestreams.CreateLiveStream,
        admin: Mapping = Depends(get_current_admin),
) -> Optional[Mapping]:
    return await livestream.create(stream)
