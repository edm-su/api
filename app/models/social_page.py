from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


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
