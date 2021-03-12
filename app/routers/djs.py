from typing import Mapping

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
) -> dj_schema.DJ:
    if await dj_crud.find(name=dj.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Такой DJ уже существует',
        )
    db_dj = await dj_crud.create(dj)
    if dj.group_members:
        group_members = await dj_crud.get_group_members(db_dj['id'])
        return dj_schema.DJ(
            group_members=[member['slug'] for member in group_members],
            **db_dj,
        )
    return dj_schema.DJ(**db_dj)
