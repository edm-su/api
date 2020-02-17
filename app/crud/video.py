from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.video import Video
from app.models.user import User


def get_videos_count(db: Session, parent=None):
    if parent:
        videos = parent.videos.filter_by(deleted=False).count()
    else:
        videos = db.query(Video).filter_by(deleted=False).count()
    return videos


def get_videos(db: Session, skip: int = 0, limit: int = 25, parent=None, deleted: bool = False, user: User = None):
    if parent:
        videos = parent.videos.filter_by(deleted=deleted).order_by(desc('date')).offset(skip).limit(limit).all()
    else:
        videos = db.query(Video).filter_by(deleted=deleted).order_by(desc('date')).offset(skip).limit(
            limit).all()
    for video in videos:
        video.liked = check_like(user, video)
    return videos


def get_related_videos(title: str, db: Session, limit: int = 25, user: User = None):
    videos = db.query(Video).filter_by(deleted=False).order_by(Video.title.op('<->')(title)).limit(
        limit).offset(1).all()
    for video in videos:
        video.liked = check_like(user, video)
    return videos


def get_liked_videos(db: Session, user: User):
    return user.liked_videos


def add_liked_video(db: Session, user: User, video: Video):
    user.liked_videos.append(video)
    db.commit()
    db.refresh(user)
    return True


def delete_liked_video(db: Session, user: User, video: Video):
    user.liked_videos.remove(video)
    db.commit()
    db.refresh(user)
    return True


def get_video_by_slug(db: Session, slug: str, deleted: bool = False, user: User = None):
    video = db.query(Video).filter_by(slug=slug).filter_by(deleted=deleted).first()
    if video:
        video.liked = check_like(user, video)
    return video


def delete_video(db: Session, video: Video):
    video.deleted = True
    db.add(video)
    db.commit()
    db.refresh(video)
    return True


def check_like(user, video):
    return bool(user and video in user.liked_videos)
