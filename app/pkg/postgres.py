import datetime
from collections.abc import AsyncGenerator
from typing import Any, ClassVar

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import ARRAY, JSON, String

from app.internal.entity.settings import settings

async_engine = create_async_engine(
    str(settings.database_url),
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session, session.begin():
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map: ClassVar[dict[type, type | ARRAY]] = {
        dict[str, Any]: JSON,
        list[str]: ARRAY(String),
    }


LikedVideos = liked_videos = Table(
    "liked_videos",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("video_id", ForeignKey("videos.id"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now()),
    UniqueConstraint("user_id", "video_id", name="unique_liked_video"),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    is_active: Mapped[bool | None] = mapped_column(server_default="f")
    activation_code: Mapped[str | None] = mapped_column()
    recovery_code: Mapped[str | None] = mapped_column()
    recovery_code_lifetime_end: Mapped[
        datetime.datetime | None
    ] = mapped_column()
    is_admin: Mapped[bool | None] = mapped_column(server_default="f")
    is_banned: Mapped[bool | None] = mapped_column(server_default="f")
    created: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    tokens: Mapped[list["UserToken"]] = relationship(back_populates="user")
    liked_videos: Mapped[list["Video"]] = relationship(
        secondary=liked_videos,
        back_populates="users",
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    annotation: Mapped[str | None] = mapped_column()
    text: Mapped[dict[str, Any]] = mapped_column()
    slug: Mapped[str] = mapped_column(unique=True)
    published_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    thumbnail: Mapped[str | None] = mapped_column()
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
    )

    user: Mapped["User"] = relationship(
        back_populates="posts",
        cascade="all, delete",
    )


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column(unique=True)
    date: Mapped[datetime.date | None] = mapped_column()
    yt_id: Mapped[str] = mapped_column(unique=True)
    yt_thumbnail: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column(server_default="0")
    deleted: Mapped[bool | None] = mapped_column(server_default="f")

    users: Mapped[list["User"]] = relationship(
        secondary=liked_videos,
        back_populates="liked_videos",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="video",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    published_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    deleted: Mapped[bool | None] = mapped_column(server_default="f")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(
        back_populates="comments",
        cascade="all, delete",
    )
    video: Mapped["Video"] = relationship(
        back_populates="comments",
        cascade="all, delete",
    )


class LiveStream(Base):
    __tablename__ = "livestreams"
    __table_args__ = (
        UniqueConstraint(
            "start_time",
            "slug",
            name="unique_livestream",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column(index=True)
    cancelled: Mapped[bool | None] = mapped_column(server_default="f")
    start_time: Mapped[datetime.datetime] = mapped_column()
    end_time: Mapped[datetime.datetime | None] = mapped_column()
    image: Mapped[str | None] = mapped_column()
    url: Mapped[str | None] = mapped_column()
    genres: Mapped[list[str] | None] = mapped_column()


class UserToken(Base):
    __tablename__ = "users_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
    expired_at: Mapped[datetime.datetime | None] = mapped_column()
    revoked_at: Mapped[datetime.datetime | None] = mapped_column()
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(
        back_populates="tokens",
        cascade="all, delete",
    )
