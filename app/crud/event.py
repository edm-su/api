from sqlalchemy.orm import Session



def get_events(db: Session, skip: int = 0, limit: int = 25):
    return db.query(Event).offset(skip).limit(limit).all()


def get_event(db: Session, slug: str):
    return db.query(Event).filter_by(slug=slug).first()
