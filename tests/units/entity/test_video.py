import pytest
from faker import Faker
from typing_extensions import Self

from edm_su_api.internal.entity.video import (
    DeleteType,
    NewVideoDto,
    UpdateVideoDto,
    Video,
)


class TestNewVideoDto:
    @pytest.fixture
    def new_video(self: Self, faker: Faker) -> NewVideoDto:
        return NewVideoDto(
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            yt_id=faker.word(),
            yt_thumbnail=faker.url(),
            duration=faker.pyint(),
            slug=faker.slug(),
        )

    def test_expand_slug(self: Self, new_video: NewVideoDto) -> None:
        original_slug = new_video.slug
        new_video.expand_slug()
        assert new_video.slug != original_slug

    def test_generate_slug_when_not_provided(self: Self, faker: Faker) -> None:
        """Test that the slug is generated from the title when not provided."""
        title = faker.word()
        video = NewVideoDto(
            title=title,
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            yt_id=faker.word(),
            yt_thumbnail=faker.url(),
            duration=faker.pyint(),
        )
        assert video.slug == title.lower()


class TestUpdateVideoDto:
    @pytest.fixture
    def update_video(self: Self, faker: Faker) -> UpdateVideoDto:
        return UpdateVideoDto(
            id=faker.pyint(),
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
        )

    def test_expand_slug(self: Self, update_video: UpdateVideoDto) -> None:
        """Test that expand_slug method modifies the slug correctly."""
        assert update_video.slug
        original_slug = update_video.slug
        update_video.expand_slug()
        assert update_video.slug != original_slug
        assert update_video.slug.endswith(original_slug)
        # Check that prefix is 8 characters hex
        prefix = update_video.slug.split("-")[0]
        assert len(prefix) == 8
        int(prefix, 16)  # Will raise ValueError if not hex

    def test_generate_slug_when_not_provided(self: Self, faker: Faker) -> None:
        """Test that the slug is generated from the title when not provided."""
        title = faker.word()
        video = UpdateVideoDto(
            id=faker.pyint(),
            title=title,
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
        )
        assert video.slug == title.lower()

    def test_custom_slug_is_preserved(self: Self, faker: Faker) -> None:
        """Test that a custom provided slug is not overridden."""
        custom_slug = faker.slug()
        video = UpdateVideoDto(
            id=faker.pyint(),
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            slug=custom_slug,
        )
        assert video.slug == custom_slug


class TestVideo:
    @pytest.fixture
    def video(self: Self, faker: Faker) -> Video:
        return Video(
            id=faker.pyint(),
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            yt_id=faker.word(),
            yt_thumbnail=faker.url(),
            duration=faker.pyint(),
            slug=faker.slug(),
            is_favorite=faker.boolean(),
            is_blocked_in_russia=faker.boolean(),
        )

    def test_default_deletion_fields(self: Self, video: Video) -> None:
        """Test that deletion fields have correct default values."""
        assert video.deleted is False
        assert video.delete_type is None

    def test_deletion_fields_serialization(self: Self, faker: Faker) -> None:
        """Test that deletion fields are properly serialized."""
        video = Video(
            id=faker.pyint(),
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            yt_id=faker.word(),
            yt_thumbnail=faker.url(),
            duration=faker.pyint(),
            slug=faker.slug(),
            is_favorite=faker.boolean(),
            is_blocked_in_russia=faker.boolean(),
            deleted=True,
            delete_type=DeleteType.TEMPORARY,
        )

        # Convert to dict to simulate serialization
        serialized = video.model_dump()

        # Check that deletion fields are included in serialized output
        assert serialized["deleted"] is True
        assert serialized["delete_type"] == DeleteType.TEMPORARY
