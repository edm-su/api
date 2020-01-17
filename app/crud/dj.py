from sqlalchemy.orm import Session

from app.models.dj import Dj


def get_djs(db: Session, skip: int = 0, limit: int = 25):
    return db.query(Dj).offset(skip).limit(limit).all()


def get_dj(db: Session, slug: str):
    return db.query(Dj).filter_by(slug=slug).first()
