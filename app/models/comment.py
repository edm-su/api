from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, event
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    deleted = Column(Boolean, default=False)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='comments')
    video = relationship('Video', back_populates='comments')

    def __init__(self, user, video, text):
        self.user = user
        self.video = video
        self.text = text

    def __repr__(self):
        return f'Comment({self.text}, {self.published_at})'


@event.listens_for(Comment, 'before_insert')
def add_published_time_for_comments(mapper, connection, target):
    target.published_at = datetime.now()
