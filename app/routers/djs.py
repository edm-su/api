from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.utils import get_db

router = APIRouter()


@router.get('/djs/', response_model=List[schemas.Dj], tags=['DJs'], summary='Получить список диджеев')
def read_djs(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    djs = crud.get_djs(db, skip, limit)
    return djs


@router.get('/djs/{slug}', response_model=schemas.Dj, tags=['DJs'], summary='Получить диджея')
def read_dj(slug: str, db: Session = Depends(get_db)):
    dj = crud.get_dj(db, slug)
    if dj:
        return dj
    else:
        raise HTTPException(status_code=404, detail='Диджей не найден')
