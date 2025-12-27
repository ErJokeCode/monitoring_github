from fastapi import APIRouter

from .github_events import router as task_router

api_router = APIRouter(prefix='/v1')

api_router.include_router(task_router)
