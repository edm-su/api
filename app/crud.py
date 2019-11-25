from sqlalchemy.orm import Session

from app import models


def get_channels(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Channel).offset(skip).limit(limit).all()


def get_channel(db: Session, slug: str):
    return db.query(models.Channel).filter_by(slug=slug).first()


def get_events(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Event).offset(skip).limit(limit).all()


def get_event(db: Session, slug: str):
    return db.query(models.Event).filter_by(slug=slug).first()
