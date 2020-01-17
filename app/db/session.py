from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker

from app import settings

connect_url = URL(drivername=settings.DB_DRIVER,
                  username=settings.DB_USERNAME,
                  password=settings.DB_PASSWORD,
                  host=settings.DB_HOST,
                  port=settings.DB_PORT,
                  database=settings.DB_NAME)

engine = create_engine(connect_url, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
