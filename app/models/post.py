from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    annotation = Column(String)
    text = Column(Text, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    thumbnail = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='posts')

    def __init__(self, title, annotation, text, published_at, thumbnail, user):
        self.title = title
        self.annotation = annotation
        self.text = text
        self.published_at = published_at
        self.thumbnail = thumbnail
        self.user = user

    def __repr__(self):
        return f'Post({self.title}, {self.slug}, {self.published_at})'
