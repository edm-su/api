from typing import Annotated

from fastapi import Depends, Query
from typing_extensions import Self


class Paginator:
    def __init__(
        self: Self,
        skip: Annotated[
            int,
            Query(ge=0),
        ] = 0,
        limit: Annotated[
            int,
            Query(ge=1, le=50),
        ] = 25,
    ) -> None:
        self.skip = skip
        self.limit = limit


PaginatorDeps = Annotated[Paginator, Depends(Paginator)]
