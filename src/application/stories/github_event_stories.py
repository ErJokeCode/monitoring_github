import asyncio
from datetime import datetime
import json
import logging
from typing import Any, Optional
import uuid

import aiohttp
from fastapi import WebSocket, WebSocketDisconnect

from domain.interfaces.github_event import IGitHubEventRepo
from infrastructure.nats_manager import NATSClient
from .base import BaseStory
from infrastructure.database.models import EventType, GitHubEvent
from infrastructure.ws_manager import WSManager
from ..schemes.task import GitHubOut
from ..schemes.base import ListDTO
from uuid import UUID
from config import settings

_log = logging.getLogger(__name__)


class TaskStories(BaseStory):

    repo: IGitHubEventRepo
    ws_manager: WSManager
    nats_client: NATSClient
    
    @property
    def base_url(self) -> str:
        return "https://api.github.com"
    
    async def _make_request(
        self, 
        endpoint: str, 
        owner: str, 
        repo: str,
        params: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/repos/{owner}/{repo}/{endpoint}"
        
        headers = {
            'Authorization': f"token {settings.GITHUB_TOKEN}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers, params=params)

            return await response.json()
        
    async def get_commits(
        self
    ):
        return await self._make_request(endpoint="commits", owner=settings.GITHUB_OWNER, repo=settings.GITHUB_REPO)
    
    async def get_releases(
        self
    ):
        return await self._make_request(endpoint="releases", owner=settings.GITHUB_OWNER, repo=settings.GITHUB_REPO)
    
    async def get_issues(
        self
    ):
        return await self._make_request(endpoint="issues", owner=settings.GITHUB_OWNER, repo=settings.GITHUB_REPO)
    
    async def _send_ws_message(
        self, 
        type: str,
        id: UUID | None = None,
    ):
        message: dict[str, Any] = {"type": type}
        if id is not None:
            message["id"] = str(id)
        await self.ws_manager.broadcast(message=message)
        
    
    async def _publish_nats_message(
        self, 
        type: str,
        data: dict[str, Any],
    ):
        message: dict[str, Any] = {**data, "type": type}
        await self.nats_client.publish(data=message)
        
        

    async def get_by_id(
        self, 
        id: UUID
    ) -> GitHubOut:
        res = await self.repo.get(id=id)
        obj_out = GitHubOut.model_validate(res)
        
        await self._send_ws_message(type="get_by_id", id=obj_out.id)
        
        return obj_out
    
    async def get_all(
        self,
        search: str | None = None,
        sort_by: str | None = None,
        desc: int = 0,
        page: int = 1,
        limit: int = -1
    ) -> ListDTO[GitHubOut]:
        res = await self.repo.all_list(
            search=search,
            search_by=["name"],
            sort_by=sort_by,
            desc=desc,
            page=page,
            limit=limit
        )
        await self._send_ws_message(type="get_all")
        return ListDTO[GitHubOut].model_validate(res)
    
    async def create(
        self, 
        **data: Any
    ) -> GitHubOut:
        obj = GitHubEvent(
            **data
        )
        
        await self.repo.save(objs=obj)
        
        obj_out = GitHubOut.model_validate(obj)
        
        await self._send_ws_message(type="create", id=obj_out.id)
        await self._publish_nats_message(type="create", data=obj_out.model_dump(mode="json"))
        
        return obj_out
        
    async def update(
        self, 
        id: UUID,
        **data: Any
    ) -> GitHubOut:
        obj = await self.repo.get(id=id)
            
        for key, value in data.items():
            setattr(obj, key, value)
                
        await self.repo.update(obj=obj)
        
        obj_out = GitHubOut.model_validate(obj)
        
        await self._send_ws_message(type="update", id=obj_out.id)
        await self._publish_nats_message(type="update", data=obj_out.model_dump(mode="json"))
        
        return obj_out
    
    async def delete(
        self, 
        id: UUID
    ) -> None:
        await self._send_ws_message(type="delete", id=id)
        await self._publish_nats_message(type="delete", data={"id": str(id)})
        return await self.repo.delete(id=id)
    
    async def ws_connect(self, websocket: WebSocket):
        id = str(uuid.uuid4())
        await self.ws_manager.connect(id, websocket)
        
        try:
            while True:
                await self.ws_manager.receive_text(websocket)
        except WebSocketDisconnect:
            self.ws_manager.disconnect(id)
    
    async def get_from_repo(self):
        commits = await self.get_commits()
        issues = await self.get_issues()
        releases = await self.get_releases()
        
        for commit in commits:
            commit_obj = await self.repo.get_or_none(
                event_id=str(commit["sha"])
            )
            
            if commit_obj is None:
                await self.create(
                    event_id=str(commit["sha"]),
                    event_type=EventType.COMMIT,
                    title=commit["commit"]["message"].split("\n")[0],
                    description=commit["commit"]["message"],
                    author=commit["commit"]["author"]["name"],
                    url=commit["html_url"],
                    repository=settings.GITHUB_REPO,
                    commit_hash=commit["sha"],
                    raw_data=json.dumps(commit)
                )
                
        for issue in issues:
            issue_obj = await self.repo.get_or_none(
                event_id=str(issue["number"])
            )
            
            if issue_obj is None:
                await self.create(
                    event_id=str(issue["number"]),
                    event_type=EventType.ISSUE,
                    title=issue["title"],
                    description=issue["body"],
                    author=issue["user"]["login"],
                    url=issue["html_url"],
                    repository=settings.GITHUB_REPO,
                    issue_number=int(issue["number"]),
                    raw_data=json.dumps(issue)
                )
        
        for releas in releases:
            release_obj = await self.repo.get_or_none(
                event_id=releas["tag_name"]
            )
            
            if release_obj is None:
                await self.create(
                    event_id=releas["tag_name"],
                    event_type=EventType.RELEASE,
                    title=releas["name"],
                    description=releas["body"],
                    author=releas["author"]["login"],
                    url=releas["html_url"],
                    repository=settings.GITHUB_REPO,
                    release_version=releas["tag_name"],
                    raw_data=json.dumps(releas)
                )
                
        return {"status": "ok"}
                    
    async def periodic_task(self, interval_seconds: int = 60):
        """Фоновая задача, выполняющаяся раз в interval_seconds секунд"""
        while True:
            try:
                _log.info("Выполняется фоновая задача")
                async with self.begin() as stories:
                    await stories.get_from_repo()
                
            except Exception as e:
                print(f"Ошибка в фоновой задаче: {e}")
            
            await asyncio.sleep(interval_seconds)