from datetime import date, timedelta
from typing import Mapping, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

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


@router.get('/')
async def get_streams(
        start: date = Query(date.today() - timedelta(days=2)),
        end: date = Query(date.today() + timedelta(days=31)),
) -> list[Mapping]:
    if start + timedelta(days=45) < end:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'Период не может превышать 45 дней',
        )
    return await livestream.find(start, end)
