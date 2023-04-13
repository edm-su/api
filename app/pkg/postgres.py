from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings

async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)
