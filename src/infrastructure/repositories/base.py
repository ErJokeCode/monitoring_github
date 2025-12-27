import logging
from typing import Any, Sequence, Type, TypeVar
from sqlalchemy import Select, String, cast, delete, select, update, asc,  desc as func_desc, func,  or_
from ..context import StoryContext
from sqlalchemy.orm import DeclarativeBase, class_mapper
from sqlalchemy.orm.interfaces import LoaderOption

from domain.interfaces.base import IBaseRepo
from application.schemes.base import ListDTO
from ..exceptions import FieldException, PageNotFoundException, EntityNotFoundException
    
_log = logging.getLogger(__name__)

Aggregate = TypeVar("Aggregate", bound=DeclarativeBase)


class BaseRepo(IBaseRepo[Aggregate]):
    def __init__(self):

        if not hasattr(self, "model"):
            raise ValueError("Model not found")

        self.model: Type[Aggregate] = getattr(self, "model")

        self.pks = [
            column.key for column in class_mapper(self.model).primary_key
        ]

        self.relationships = [
            column.key for column in class_mapper(self.model).relationships
        ]

    @property
    def session(self):
        return StoryContext.get_current_session()

    async def all(self, **filters: Any) -> list[Aggregate]:
        """Получает все записи"""
        stmt = select(
            self.model
        ).filter_by(
            **filters
        )

        result = await self.session.execute(stmt)
        return [entity for entity in result.scalars().all()]

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
        if stmt is None:
            stmt = select(
                self.model
            )

        if search and search_by:
            search_conditions = []
            for field in search_by:
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    search_conditions.append(  # type: ignore
                        # type: ignore
                        cast(column, String).ilike(f"%{search}%"))
                else:
                    raise FieldException(
                        f"Поле {field} для поиска не найдено"
                    )

            if search_conditions:
                stmt = stmt.filter(
                    or_(*search_conditions))  # type: ignore

        if filters:
            stmt = stmt.filter_by(**filters)

        if page < 1:
            raise PageNotFoundException(
                "Номер страницы должен быть больше 0"
            )

        stmt_total_record = stmt

        if sort_by:
            if hasattr(self.model, sort_by):
                stmt = stmt.order_by(
                    func_desc(getattr(self.model, sort_by)) if desc == 1 else asc(
                        getattr(self.model, sort_by))
                )
            else:
                raise FieldException(
                    f"Поле {sort_by} для сортировки не найдено"
                )

        stmt = stmt.offset((page - 1) * limit)
        if limit != -1:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        content = result.scalars().all()

        stmt_total_record = stmt_total_record.with_only_columns(
            # type: ignore
            func.count(*[getattr(self.model, pk) for pk in self.pks]))  # type: ignore
        stmt_total_record = await self.session.execute(stmt_total_record)
        total_record = stmt_total_record.scalar_one_or_none()  # type: ignore

        if total_record is None:
            total_record = 0

        if limit == -1:
            pages = 1
        else:
            pages = total_record // limit if total_record % limit == 0 else total_record // limit + 1

        return ListDTO[Aggregate](
            page_number=page,
            page_size=limit if limit != -1 else total_record,
            total_pages=pages,
            total_record=total_record,
            content=[entity for entity in content],
        )
    
    async def get_or_none(self, **filters: Any) -> Aggregate | None:
        """Получает запись"""
        stmt = select(
            self.model
        ).filter_by(
            **filters
        )

        result = await self.session.execute(stmt)
        entity = result.scalars().first()

        if entity is None:
            return None

        return entity

    async def get(self, **filters: Any) -> Aggregate:
        """Получает запись"""
        entity = await self.get_or_none(**filters)

        if entity is None:
            raise EntityNotFoundException("Объект не найден")

        return entity

    async def save(self, objs: list[Aggregate] | Aggregate) -> None:
        """Сохраняет запись в БД, без relationship."""
        if not isinstance(objs, list):
            objs = [objs]
        self.session.add_all(objs)
        await self.session.flush()
        
    async def get_or_create(self, data: dict[str, Any] | None = None, **filters: Any) -> Aggregate:
        get_obj = await self.get_or_none(**filters)
        
        if get_obj is not None:
            return get_obj
        
        if not data:
            data = {}
        data = {**data, **filters}
        obj = self.model(**data)
        
        await self.save(obj)
        
        return obj
        
    async def update(self, obj: Aggregate) -> None:
        await self.session.flush()
        
    async def update_fields(self, fields: dict[str, Any], **filters: Any) -> None:
        stmt = update(
            self.model
        ).filter_by(
            **filters
        ).values(
            **fields
        )
        await self.session.execute(stmt)
        
        await self.session.flush()

    async def delete(self, **filters: Any) -> None:
        """Удаляет запись в БД."""
        query = delete(
            self.model
        ).filter_by(
            **filters
        )
        await self.session.execute(query)

        await self.session.flush()

    async def exist(self, **filters: Any) -> bool:
        stmt = select(
            self.model
        ).filter_by(
            **filters
        )

        result = await self.session.execute(stmt)
        entity = result.scalars().first()

        return entity is not None
