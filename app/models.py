from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database import Base


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

    videos = relationship('Video', back_populates='channel', lazy='dynamic')

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"<Channel('{self.name}', '{self.slug}', '{self.image}'"


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

    videos = relationship('Video', back_populates='event')

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"Event('{self.name}', '{self.slug}', '{self.image}')"


djs_videos_table = Table('djs_videos', Base.metadata,
                         Column('dj_id', Integer, ForeignKey('djs.id')),
                         Column('video_id', Integer, ForeignKey('videos.id'))
                         )


class Dj(Base):
    __tablename__ = 'djs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

    videos = relationship('Video', back_populates='djs', secondary=djs_videos_table)

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"Dj('{self.name}', '{self.slug}', '{self.image}')"


class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    date = Column(Date)
    yt_id = Column(String, nullable=False, unique=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    channel_id = Column(Integer, ForeignKey('channels.id'))

    djs = relationship('Dj', back_populates='videos', secondary=djs_videos_table)
    event = relationship('Event', back_populates='videos')
    channel = relationship('Channel', back_populates='videos')

    def __init__(self, title, slug, date, yt_id):
        self.title = title
        self.slug = slug
        self.date = date
        self.yt_id = yt_id

    def __repr__(self):
        return f"Video('{self.title}', '{self.slug}', '{self.date}', '{self.yt_id}')"
