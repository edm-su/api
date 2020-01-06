from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine.url import URL

from app import settings

connect_url = URL(drivername=settings.DB_DRIVER,
                  username=settings.DB_USERNAME,
                  password=settings.DB_PASSWORD,
                  host=settings.DB_HOST,
                  port=settings.DB_PORT,
                  database=settings.DB_NAME)

engine = create_engine(
    connect_url
)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
