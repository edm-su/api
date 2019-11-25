from sqlalchemy import Column, Integer, String

from app.database import Base


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

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

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"Event('{self.name}', '{self.slug}', '{self.image}')"


class Dj(Base):
    __tablename__ = 'djs'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    image = Column(String, unique=True, nullable=False)

    def __init__(self, name, slug, image):
        self.name = name
        self.slug = slug
        self.image = image

    def __repr__(self):
        return f"Dj('{self.name}', '{self.slug}', '{self.image}')"
