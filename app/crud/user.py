from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import User, get_password_hash, generate_secret_code
from app.schemas.user import CreateUser


def create_user(db: Session, user: CreateUser):
    hashed_password = get_password_hash(user.password)
    db_user = User(user.username, user.email, hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user


def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    return user


def get_user_by_id(db: Session, _id: int):
    user = db.query(User).get(_id)
    return user


def get_user_by_recovery_code(db: Session, code: str):
    now = datetime.now()
    user = db.query(User).filter(User.recovery_code == code).filter(User.recovery_code_lifetime_end > now).first()
    return user


def activate_user(db: Session, code: str):
    user = db.query(User).filter(User.is_active == False).filter(
        User.activate_code == code).first()
    if user:
        user.is_active = True
        user.activate_code = ''
        db.add(user)
        db.commit()
    return user


def generate_recovery_user_code(db: Session, user: User):
    user.recovery_code = generate_secret_code()
    user.recovery_code_lifetime_end = datetime.now() + timedelta(days=2)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.recovery_code


def change_password(db: Session, user: User, password: str, recovery: bool = False):
    user.password = get_password_hash(password)
    if recovery:
        user.recovery_code = None
        user.recovery_code_lifetime_end = None
    db.add(user)
    db.commit()
    return user
