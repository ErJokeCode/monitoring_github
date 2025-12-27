from abc import ABC, abstractmethod
from typing import Any, Generic, List, Type, TypeVar
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Select
from application.schemes.base import ListDTO

Aggregate = TypeVar("Aggregate", bound=DeclarativeBase)


class IBaseRepo(ABC, Generic[Aggregate]):
    model: Type[Aggregate]
    
    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def all(self, **kwargs: Any) -> List[Aggregate]:
        raise NotImplementedError

    @abstractmethod
    async def all_list(
        self,
        search: str | None = None,
        search_by: list[str] | None = None,
        sort_by: str | None = None,
        desc: int = 0,
        page: int = 1,
        limit: int = -1,
        stmt: Select[Any] | None = None,
        **filters: Any
    ) -> ListDTO[Aggregate]:
        raise NotImplementedError

    @abstractmethod
    async def get(self, **filters: Any) -> Aggregate:
        raise NotImplementedError

    @abstractmethod
    async def get_or_none(self, **filters: Any) -> Aggregate | None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_or_create(self, data: dict[str, Any] | None = None, **filters: Any) -> Aggregate:
        raise NotImplementedError

    @abstractmethod
    async def save(self, objs: list[Aggregate] | Aggregate) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, obj: Aggregate) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def update_fields(self, fields: dict[str, Any], **filters: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **filters: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exist(self, **filters: Any) -> bool:
        raise NotImplementedError
