import random
import string
from os import getenv
from datetime import datetime

from algoliasearch.search_client import SearchClient
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Table, Index, event, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


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

    djs = relationship('Dj', back_populates='videos', secondary=djs_videos_table)
    event = relationship('Event', back_populates='videos')
    channel = relationship('Channel', back_populates='videos')
    genres = relationship('Genre', back_populates='videos', secondary=videos_genres_table)
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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    activate_code = Column(String)
    recovery_code = Column(String)
    recovery_code_lifetime_end = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created = Column(DateTime, nullable=False)
    last_login = Column(DateTime)
    last_login_ip = Column(String)

    comments = relationship('Comment', back_populates='user')

    def __init__(self, username, email, password, is_admin=False, is_activate=False):
        self.username = username
        self.email = email
        self.password = password
        self.activate_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.created = datetime.now()
        self.is_active = is_activate
        self.is_admin = is_admin

    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.is_banned}, {self.is_admin}, {self.is_active})'


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


@event.listens_for(Video, 'after_insert')
def add_video_to_algolia_index(mapper, connection, target):
    client = SearchClient.create(getenv('ALGOLIA_APP_ID'), getenv('ALGOLIA_API_KEY'))
    index = client.init_index(getenv('ALGOLIA_INDEX'))
    index.save_object({'objectID': target.id, 'title': target.title, 'date': target.date, 'slug': target.slug,
                       'thumbnail': target.yt_thumbnail})


@event.listens_for(Comment, 'before_insert')
def add_published_time_for_comments(mapper, connection, target):
    target.published_at = datetime.now()


@event.listens_for(User, 'after_insert')
def send_activation_email(mapper, connection, target):
    if not target.is_admin or not target.is_active:
        from tasks import send_activate_email
        send_activate_email.delay(target.email, target.activate_code)
