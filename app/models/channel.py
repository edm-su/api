from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    yt_id = Column(String, nullable=False, unique=True)
    yt_thumbnail = Column(String, nullable=False)
    yt_banner = Column(String)

    videos = relationship('Video', back_populates='channel', lazy='dynamic')

    def __init__(self, name, slug, yt_id, yt_thumbnail, yt_banner=None):
        self.name = name
        self.slug = slug
        self.yt_id = yt_id
        self.yt_thumbnail = yt_thumbnail
        self.yt_banner = yt_banner

    def __repr__(self):
        return f"<Channel('{self.name}', '{self.slug}')>"
