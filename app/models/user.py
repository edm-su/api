import hashlib
import random
import string
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, event
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app import settings


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


@event.listens_for(User, 'after_insert')
def send_activation_email(mapper, connection, target):
    if not target.is_admin or not target.is_active:
        from tasks import send_activate_email
        send_activate_email.delay(target.email, target.activate_code)


def get_password_hash(password):
    return hashlib.sha256(f'{password}{settings.SECRET_KEY}'.encode()).hexdigest()


def generate_secret_code(n: int = 10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
