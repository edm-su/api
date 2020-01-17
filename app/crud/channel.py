from sqlalchemy.orm import Session

from app.models.channel import Channel


def get_channel(db: Session, slug: str):
    return db.query(Channel).filter_by(slug=slug).first()


def get_channels(db: Session, skip: int = 0, limit: int = 25):
    return db.query(Channel).offset(skip).limit(limit).all()
