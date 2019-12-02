from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.database import Base


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    youtube_id = Column(String, nullable=False, unique=True)
    thumbnail_url = Column(String, nullable=False)

    videos = relationship('Video', back_populates='channel', lazy='dynamic')

    def __init__(self, name, slug, youtube_id, thumbnail_url):
        self.name = name
        self.slug = slug
        self.youtube_id = youtube_id
        self.thumbnail_url = thumbnail_url

    def __repr__(self):
        return f"<Channel('{self.name}', '{self.slug}', '{self.youtube_id}', '{self.thumbnail_url}')"


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

    videos = relationship('Video', back_populates='event', lazy='dynamic')

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"Event('{self.name}', '{self.slug}', '{self.image}')"


class SocialPage(Base):
    __tablename__ = 'social_pages'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    network = Column(String, nullable=False)
    dj_id = Column(Integer, ForeignKey('djs.id'), nullable=False)

    dj = relationship('Dj', back_populates='social_pages')

    def __init__(self, url, network):
        self.url = url
        self.network = network


djs_videos_table = Table('djs_videos', Base.metadata,
                         Column('dj_id', Integer, ForeignKey('djs.id')),
                         Column('video_id', Integer, ForeignKey('videos.id'))
                         )

videos_genres_table = Table('videos_genres', Base.metadata,
                            Column('video_id', Integer, ForeignKey('videos.id')),
                            Column('genre_id', Integer, ForeignKey('genres.id'))
                            )

djs_genres_table = Table('djs_genres', Base.metadata,
                         Column('dj_id', Integer, ForeignKey('djs.id')),
                         Column('genre_id', Integer, ForeignKey('genres.id'))
                         )


class Dj(Base):
    __tablename__ = 'djs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)
    country = Column(String)

    videos = relationship('Video', back_populates='djs', secondary=djs_videos_table)
    social_pages = relationship('SocialPage', back_populates='dj')
    genres = relationship('Genre', back_populates='djs', secondary=djs_genres_table)

    def __init__(self, name, slug, image, country=None):
        self.name = name
        self.slug = slug
        self.image = image
        self.country = country

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
    genres = relationship('Genre', back_populates='videos', secondary=videos_genres_table)

    def __init__(self, title, slug, date, yt_id):
        self.title = title
        self.slug = slug
        self.date = date
        self.yt_id = yt_id

    def __repr__(self):
        return f"Video('{self.title}', '{self.slug}', '{self.date}', '{self.yt_id}')"


class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)

    videos = relationship('Video', back_populates='genres', secondary=videos_genres_table)
    djs = relationship('Dj', back_populates='genres', secondary=djs_genres_table)

    def __init__(self, name, slug):
        self.name = name
        self.slug = slug
