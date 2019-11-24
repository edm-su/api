from sqlalchemy.orm import Session

from app import models


def get_channels(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Channel).offset(skip).limit(limit).all()
