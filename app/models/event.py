from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


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
