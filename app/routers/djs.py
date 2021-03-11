from typing import Optional, Mapping

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.auth import get_current_admin
from app.crud import dj as dj_crud
from app.schemas import dj as dj_schema

router = APIRouter(prefix='/djs', tags=['Диджеи'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=dj_schema.DJ,
)
async def create_dj(
        dj: dj_schema.CreateDJ,
        admin: Mapping = Depends(get_current_admin),
) -> Optional[Mapping]:
    if await dj_crud.find(name=dj.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Такой DJ уже существует',
        )
    return await dj_crud.create(dj)
