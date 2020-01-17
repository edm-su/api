from sqlalchemy import event, Index, Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.dj import djs_videos_table

from app.utils import algolia_client


class Video(Base):
    __tablename__ = 'videos'
    __table_args__ = (
        Index('title_idx', 'title',
              postgresql_ops={'title': 'gin_trgm_ops'},
              postgresql_using='gin'),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    date = Column(Date)
    yt_id = Column(String, nullable=False, unique=True)
    yt_thumbnail = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    duration = Column(Integer, default=0)
    deleted = Column(Boolean, default=False)

    djs = relationship('Dj', back_populates='videos', secondary=djs_videos_table)
    event = relationship('Event', back_populates='videos')
    channel = relationship('Channel', back_populates='videos')
    comments = relationship('Comment', back_populates='video')

    def __init__(self, title, slug, date, yt_id, yt_thumbnail, duration=0):
        self.title = title
        self.slug = slug
        self.date = date
        self.yt_id = yt_id
        self.yt_thumbnail = yt_thumbnail
        self.duration = duration

    def __repr__(self):
        return f"Video('{self.title}', '{self.slug}', '{self.date}', '{self.yt_id}')"


@event.listens_for(Video, 'after_insert')
def add_video_to_algolia_index(mapper, connection, target):
    index = algolia_client()
    index.save_object({'objectID': target.id, 'title': target.title, 'date': target.date, 'slug': target.slug,
                       'thumbnail': target.yt_thumbnail})


@event.listens_for(Video, 'after_update')
def delete_video(mapper, connection, target):
    if target.deleted:
        index = algolia_client()
        index.delete_object(target.id)
