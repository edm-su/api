from sqlalchemy import desc
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


def get_djs(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Dj).offset(skip).limit(limit).all()


def get_dj(db: Session, slug: str):
    return db.query(models.Dj).filter_by(slug=slug).first()


def get_videos(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Video).order_by(desc('date')).offset(skip).limit(limit).all()


def get_video(db: Session, slug: str):
    return db.query(models.Video).filter_by(slug=slug).first()
