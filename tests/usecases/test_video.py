import pytest
from app.internal.service.video import (
    GetAllVideosUseCase,
    PostgresVideoRepository,
    Video,
)
from pytest_mock import MockFixture
from faker import Faker


class TestGetAllVideosUseCase:
    @pytest.fixture(autouse=True)
    def _mock_video_repository(
        self,
        mocker: MockFixture,
        faker: Faker,
    ) -> None:
        mocker.patch.object(
            PostgresVideoRepository,
            "get_all",
            return_value=[
                Video(
                    id=faker.pyint(),
                    title=faker.pystr(),
                    slug=faker.pystr(),
                    duration=faker.pyint(),
                    yt_id=faker.pystr(),
                    yt_thumbnail=f"https://i.ytimg.com/vi/{faker.pystr()}"
                    f"/default.jpg",
                    date=faker.date_between(
                        start_date="-1y",
                        end_date="today",
                    ),
                ),
            ],
        )

    @pytest.fixture
    def usecase(self) -> GetAllVideosUseCase:
        return GetAllVideosUseCase(PostgresVideoRepository())

    @pytest.mark.asyncio
    async def test_get_all_videos(
        self,
        usecase: GetAllVideosUseCase,
    ) -> None:
        videos = await usecase.execute()
        assert videos is not None
        assert len(videos) > 0
