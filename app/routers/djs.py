from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.crud import dj
from app.schemas.dj import Dj
from app.utils import get_db

router = APIRouter()


@router.get('/djs/', response_model=List[Dj], tags=['DJs'], summary='Получить список диджеев')
def read_djs(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    djs = dj.get_djs(db, skip, limit)
    return djs


@router.get('/djs/{slug}', response_model=Dj, tags=['DJs'], summary='Получить диджея')
def read_dj(slug: str, db: Session = Depends(get_db)):
    db_dj = dj.get_dj(db, slug)
    if db_dj:
        return db_dj
    else:
        raise HTTPException(status_code=404, detail='Диджей не найден')
