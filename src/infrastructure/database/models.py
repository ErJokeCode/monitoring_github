import enum
from typing import Annotated

from sqlalchemy import Enum, Integer, String, Text
from .base_model import Base
from sqlalchemy.orm import Mapped, mapped_column


str_ = Annotated[str, mapped_column(String)]

class EventType(enum.Enum):
    COMMIT = "commit"
    ISSUE = "issue"
    RELEASE = "release"

class GitHubEvent(Base):
    __tablename__ = "github_events"
    
    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    repository: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_data: Mapped[str] = mapped_column(Text) 
    
    commit_hash: Mapped[str | None] = mapped_column(String(100), nullable=True)
    issue_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    release_version: Mapped[str | None] = mapped_column(String(50), nullable=True)


