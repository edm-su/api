from datetime import datetime, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.utils import get_password_hash, generate_secret_code


# Каналы
def get_channels(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Channel).offset(skip).limit(limit).all()


def get_channel(db: Session, slug: str):
    return db.query(models.Channel).filter_by(slug=slug).first()


# События
def get_events(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Event).offset(skip).limit(limit).all()


def get_event(db: Session, slug: str):
    return db.query(models.Event).filter_by(slug=slug).first()


# Диджеи
def get_djs(db: Session, skip: int = 0, limit: int = 25):
    return db.query(models.Dj).offset(skip).limit(limit).all()


def get_dj(db: Session, slug: str):
    return db.query(models.Dj).filter_by(slug=slug).first()


# Видео
def get_videos_count(db: Session, parent=None):
    if parent:
        videos = parent.videos.count()
    else:
        videos = db.query(models.Video).count()
    return videos


def get_videos(db: Session, skip: int = 0, limit: int = 25, parent=None):
    if parent:
        videos = parent.videos.order_by(desc('date')).offset(skip).limit(limit).all()
    else:
        videos = db.query(models.Video).order_by(desc('date')).offset(skip).limit(limit).all()
    return videos


def get_related_videos(title: str, db: Session, limit: int = 25):
    videos = db.query(models.Video).order_by(models.Video.title.op('<->')(title)).limit(limit).offset(1).all()
    return videos


def get_video_by_slug(db: Session, slug: str):
    return db.query(models.Video).filter_by(slug=slug).first()


# Пользователи
def create_user(db: Session, user: schemas.CreateUser):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(user.username, user.email, hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    return db_user


def get_user_by_username(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    return db_user


def get_user_by_id(db: Session, _id: int):
    db_user = db.query(models.User).get(_id)
    return db_user


def get_user_by_recovery_code(db: Session, code: str):
    now = datetime.now()
    db_user = db.query(models.User).filter(models.User.recovery_code == code).filter(
        models.User.recovery_code_lifetime_end > now).first()
    return db_user


def activate_user(db: Session, code: str):
    db_user = db.query(models.User).filter(models.User.is_active == False).filter(
        models.User.activate_code == code).first()
    if db_user:
        db_user.is_active = True
        db_user.activate_code = ''
        db.add(db_user)
        db.commit()
    return db_user


def generate_recovery_user_code(db: Session, user: models.User):
    user.recovery_code = generate_secret_code()
    user.recovery_code_lifetime_end = datetime.now() + timedelta(days=2)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.recovery_code


def change_password(db: Session, user: models.User, password: str, recovery: bool = False):
    user.password = get_password_hash(password)
    if recovery:
        user.recovery_code = None
        user.recovery_code_lifetime_end = None
    db.add(user)
    db.commit()
    return user


# Комментарии
def create_comment(db: Session, user: models.User, video: models.Video, text: str):
    db_comment = models.Comment(user, video, text)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments(db: Session, video: models.Video):
    return video.comments
