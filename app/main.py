from typing import List

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import SessionLocal

app = FastAPI()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/channels/', response_model=List[schemas.Channel])
def read_channels(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    channels = crud.get_channels(db, skip=skip, limit=limit)
    return channels


@app.get('/events/', response_model=List[schemas.Event])
def read_events(skip: int = 0, limit: int = 25, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events
