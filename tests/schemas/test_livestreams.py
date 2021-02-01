from typing import Mapping

from app.schemas import livestreams


def test_end_date_validation(livestream_data: Mapping) -> None:
    data = dict(livestream_data)
    data['end_time'] = None
    livestreams.BaseLiveStream(**data)
