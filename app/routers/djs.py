from collections.abc import Mapping

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from starlette import status

from app.auth import get_current_admin
from app.crud import dj as dj_crud
from app.helpers import Paginator
from app.schemas import dj as dj_schema

router = APIRouter(prefix="/djs", tags=["Диджеи"])


async def find_dj(slug: str = Path(..., title="slug")) -> None | Mapping:
    dj = await dj_crud.find(slug=slug)
    if not dj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DJ не найден",
        )
    return dj


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=dj_schema.DJ,
)
async def create_dj(
    dj: dj_schema.CreateDJ,
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> dj_schema.DJ:
    errors = {}
    if await dj_crud.find(name=dj.name):
        errors["name"] = "Такой dj уже существует"
    if await dj_crud.find(slug=dj.slug):
        errors["slug"] = "Такой slug уже существует"
    if errors:
        raise HTTPException(status.HTTP_409_CONFLICT, errors)

    db_dj = await dj_crud.create(dj)
    if dj.group_members:
        group_members = await dj_crud.get_groups_members([db_dj["id"]])
        return dj_schema.DJ(
            group_members=[member["slug"] for member in group_members],
            **db_dj,
        )
    return dj_schema.DJ(**db_dj)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dj(
    dj: Mapping = Depends(find_dj),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> None:
    await dj_crud.delete(dj["id"])


@router.get("", response_model=list[dj_schema.DJ])
async def get_list(
    response: Response,
    pagination: Paginator = Depends(Paginator),
) -> list[dj_schema.DJ]:
    count = await dj_crud.count()
    response.headers["X-Pagination-Total-Count"] = str(count)
    response.headers["X-Pagination-Page-Count"] = str(count / pagination.limit)
    response.headers["X-Pagination-Current-Page"] = str(
        pagination.skip // pagination.limit + 1,
    )
    response.headers["X-Pagination-Per-Page"] = str(pagination.limit)

    result = []
    djs = await dj_crud.get_list(pagination.skip, pagination.limit)
    groups_members = await dj_crud.get_groups_members(
        [dj["id"] for dj in djs if dj["is_group"]],
    )
    members_of_groups = await dj_crud.get_members_of_groups(
        [dj["id"] for dj in djs if not dj["is_group"]],
    )
    for dj in djs:
        dj = dj_schema.DJ(**dj)  # noqa: PLW2901
        if dj.is_group:
            dj.group_members = [
                member["slug"]
                for member in groups_members
                if member["group_id"] == dj.id
            ]
        else:
            dj.member_of_groups = [
                group["slug"] for group in members_of_groups
                if group["dj_id"] == dj.id
            ]
        result.append(dj)
    return result


@router.get("/{slug}", response_model=dj_schema.DJ)
async def get(db_dj: Mapping = Depends(find_dj)) -> dj_schema.DJ:
    dj = dj_schema.DJ(**db_dj)
    if dj.is_group:
        group_members = await dj_crud.get_groups_members([dj.id])
        dj.group_members = [member["slug"] for member in group_members]
    else:
        member_of_groups = await dj_crud.get_members_of_groups([dj.id])
        dj.member_of_groups = [group["slug"] for group in member_of_groups]
    return dj


@router.patch("/{slug}", response_model=dj_schema.DJ)
async def patch(
    new_data: dj_schema.ChangeDJ,
    db_dj: Mapping = Depends(find_dj),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> dj_schema.DJ:
    changed_dj = await dj_crud.update(db_dj["id"], new_data)
    result = dj_schema.DJ(**changed_dj)
    if result.is_group:
        group_members = await dj_crud.get_groups_members([result.id])
        result.group_members = [member["slug"] for member in group_members]
    else:
        member_of_groups = await dj_crud.get_members_of_groups([result.id])
        result.member_of_groups = [group["slug"] for group in member_of_groups]

    return result
