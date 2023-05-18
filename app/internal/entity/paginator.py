from fastapi import Query
from typing_extensions import Self


class Paginator:
    def __init__(
        self: Self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=25, ge=1, le=50),
    ) -> None:
        self.skip = skip
        self.limit = limit
