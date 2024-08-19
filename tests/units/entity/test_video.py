import pytest
from faker import Faker
from typing_extensions import Self

from edm_su_api.internal.entity.video import NewVideoDto


class TestNewVideoDto:
    @pytest.fixture
    def new_video(self: Self, faker: Faker) -> NewVideoDto:
        return NewVideoDto(
            title=faker.word(),
            date=faker.date_between(
                start_date="-1y",
                end_date="now",
            ),
            yt_id=faker.uuid4(),
            yt_thumbnail=faker.url(),
            duration=faker.pyint(),
            slug=faker.slug(),
        )

    def test_expand_slug(self: Self, new_video: NewVideoDto) -> None:
        original_slug = new_video.slug
        new_video.expand_slug()
        assert new_video.slug != original_slug
