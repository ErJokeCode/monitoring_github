from fastapi import APIRouter, WebSocket
from uuid import UUID

from application import app_registry
from application.schemes.task import GitHubOut, GitHubInput, GitHubEdit
from application.schemes.base import ListDTO


router = APIRouter(prefix='/events', tags=['Events'])
    
@router.get(
    ""
)
async def get_all(
    search: str | None = None,
    sort_by: str | None = None,
    desc: int = 0,
    page: int = 1,
    limit: int = -1
) -> ListDTO[GitHubOut]:
    async with app_registry.github_stories.begin() as stories:
        objs = await stories.get_all(
            search=search,
            sort_by=sort_by,
            desc=desc,
            page=page,
            limit=limit
        )
        return objs


@router.get(
    "/{id}"
)
async def get_by_id(
    id: UUID
) -> GitHubOut:
    async with app_registry.github_stories.begin() as stories:
        obj = await stories.get_by_id(
            id=id
        )
        return obj


@router.patch(
    "/{id}"
)
async def edit(
    id: UUID,
    data: GitHubEdit
) -> GitHubOut:
    async with app_registry.github_stories.begin() as stories:
        obj = await stories.update(
            id=id,
            **data.model_dump()
        )
        return obj


@router.post(
    ""
)
async def create(
    data: GitHubInput
) -> GitHubOut:
    async with app_registry.github_stories.begin() as stories:
        obj = await stories.create(
            **data.model_dump()
        )
        return obj


@router.delete(
    "/{id}",
    status_code=204
)
async def delete(
    id: UUID
) -> None:
    async with app_registry.github_stories.begin() as stories:
        await stories.delete(
            id=id
        )
        return None
    
@router.post(
    "/task-generator/run"
)
async def run_task() -> dict[str, str]:
    async with app_registry.github_stories.begin() as stories:
        return await stories.get_from_repo()
        
@router.websocket("/ws/events")
async def ws_connect(websocket: WebSocket):
    async with app_registry.github_stories.begin() as stories:
        await stories.ws_connect(websocket)
