from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.video import Video
from app.models.user import User


def get_comments(video: Video):
    return video.comments


def create_comment(db: Session, user: User, video: Video, text: str):
    comment = Comment(user, video, text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
