import datetime
from collections.abc import AsyncGenerator
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint, text
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import ARRAY, JSON, TIMESTAMP, String

from edm_su_api.internal.entity.settings import settings

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
    type_annotation_map: ClassVar[dict[type, type | ARRAY | TIMESTAMP]] = {
        dict[str, Any]: JSON,
        list[str]: ARRAY(String),
        datetime.datetime: TIMESTAMP(timezone=True),
    }


class LikedVideos(Base):
    __tablename__ = "liked_videos"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "video_id",
            name="unique_liked_video",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.uuid_generate_v4(),
    )
    user_id: Mapped[UUID] = mapped_column()
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )

    video: Mapped["Video"] = relationship(
        "Video",
        back_populates="liked_by",
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
    user_id: Mapped[UUID] = mapped_column()


class Video(Base):
    __tablename__ = "videos"
    __table_args__ = (
        Index(
            "search_idx",
            text("id, title, date, is_blocked_in_russia, deleted"),
            postgresql_using="bm25",
            postgresql_with={"key_field": "id"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column(unique=True)
    date: Mapped[datetime.date | None] = mapped_column()
    yt_id: Mapped[str] = mapped_column(unique=True)
    yt_thumbnail: Mapped[str] = mapped_column()
    duration: Mapped[int] = mapped_column(server_default="0")
    is_blocked_in_russia: Mapped[bool] = mapped_column(server_default="f")
    deleted: Mapped[bool | None] = mapped_column(server_default="f")

    liked_by: Mapped[list["LikedVideos"]] = relationship()
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
    user_id: Mapped[UUID] = mapped_column()
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
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
