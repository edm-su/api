from collections.abc import AsyncGenerator

import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.internal.entity.settings import settings

async_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


metadata = sqlalchemy.MetaData()
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "username",
        sqlalchemy.String,
        nullable=False,
        unique=True,
    ),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, server_default="f"),
    sqlalchemy.Column("activation_code", sqlalchemy.String(10)),
    sqlalchemy.Column("recovery_code", sqlalchemy.String(10)),
    sqlalchemy.Column("recovery_code_lifetime_end", sqlalchemy.DateTime),
    sqlalchemy.Column("is_admin", sqlalchemy.Boolean, server_default="f"),
    sqlalchemy.Column("is_banned", sqlalchemy.Boolean, server_default="f"),
    sqlalchemy.Column(
        "created",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.sql.func.now(),
    ),
    sqlalchemy.Column("last_login", sqlalchemy.DateTime),
    sqlalchemy.Column("last_login_ip", sqlalchemy.String),
)
posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("annotation", sqlalchemy.String),
    sqlalchemy.Column("text", sqlalchemy.JSON, nullable=False),
    sqlalchemy.Column("slug", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("published_at", sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column("thumbnail", sqlalchemy.String),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
    ),
)
videos = sqlalchemy.Table(
    "videos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("slug", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("date", sqlalchemy.Date),
    sqlalchemy.Column("yt_id", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("yt_thumbnail", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("duration", sqlalchemy.Integer, server_default="0"),
    sqlalchemy.Column("deleted", sqlalchemy.Boolean, server_default="f"),
)
liked_videos = sqlalchemy.Table(
    "liked_videos",
    metadata,
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
    ),
    sqlalchemy.Column(
        "video_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("videos.id"),
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime,
        server_default=sqlalchemy.sql.func.now(),
    ),
    sqlalchemy.UniqueConstraint(
        "user_id",
        "video_id",
        name="unique_liked_video",
    ),
)
comments = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.Column("text", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(
        "published_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.sql.func.now(),
    ),
    sqlalchemy.Column("deleted", sqlalchemy.Boolean, server_default="f"),
    sqlalchemy.Column(
        "video_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
    ),
)
livestreams = sqlalchemy.Table(
    "livestreams",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "title",
        sqlalchemy.String(256),
        nullable=False,
        index=True,
    ),
    sqlalchemy.Column("cancelled", sqlalchemy.Boolean, server_default="f"),
    sqlalchemy.Column("start_time", sqlalchemy.DateTime(timezone=True)),
    sqlalchemy.Column("end_time", sqlalchemy.DateTime(timezone=True)),
    sqlalchemy.Column("image", sqlalchemy.String),
    sqlalchemy.Column("url", sqlalchemy.String(2083)),
    sqlalchemy.Column("slug", sqlalchemy.String, nullable=False, index=True),
    sqlalchemy.Column("genres", sqlalchemy.ARRAY(sqlalchemy.String)),
)
users_tokens = sqlalchemy.Table(
    "users_tokens",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(64), nullable=True),
    sqlalchemy.Column(
        "user_id",
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime(timezone=True),
        nullable=False,
        server_default=sqlalchemy.sql.func.now(),
    ),
    sqlalchemy.Column(
        "expired_at",
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
    ),
    sqlalchemy.Column(
        "revoked_at",
        sqlalchemy.DateTime(timezone=True),
        nullable=True,
    ),
)
