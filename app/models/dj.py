from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.social_page import SocialPage

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
    country = Column(String)

    videos = relationship('Video', back_populates='djs', secondary=djs_videos_table)
    social_pages = relationship(SocialPage, back_populates='dj')

    def __init__(self, name, slug, image, country=None):
        self.name = name
        self.slug = slug
        self.image = image
        self.country = country

    def __repr__(self):
        return f"Dj('{self.name}', '{self.slug}', '{self.image}')"
