from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.video import Video
from app.models.user import User


def get_comments_for_video(video: Video):
    return video.comments


def create_comment(db: Session, user: User, video: Video, text: str):
    comment = Comment(user, video, text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments(db: Session, limit: int = 50, skip: int = 0):
    return db.query(Comment).order_by(desc('published_at')).offset(skip).limit(limit).all()
