from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from infrastructure.database.models import EventType


class GitHubInput(BaseModel):
    event_id: str
    event_type: EventType
    title: str
    description: str
    author: str
    url: str 
    repository: str
    raw_data: str
    commit_hash: str | None
    issue_number: int | None
    release_version: str | None

    class Config:
        from_attributes = True


class GitHubOut(BaseModel):
    id: UUID
    
    event_id: str
    event_type: EventType
    title: str
    description: str
    author: str
    url: str 
    repository: str
    raw_data: str
    commit_hash: str | None
    issue_number: int | None
    release_version: str | None
    
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True


class GitHubEdit(BaseModel):
    event_id: str | None = None
    event_type: EventType | None = None
    title: str | None = None
    description: str | None = None
    author: str | None = None
    url: str | None = None
    repository: str | None = None
    raw_data: str | None = None
    commit_hash: str  | None = None
    issue_number: int  | None = None
    release_version: str  | None = None

    class Config:
        from_attributes = True
