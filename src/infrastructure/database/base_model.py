from datetime import datetime, timezone
from typing import Annotated
import uuid
from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


uuidpk = Annotated[uuid.UUID, mapped_column(
    UUID(), default=uuid.uuid4, primary_key=True)]

class Base(DeclarativeBase):
    """Базовый класс для всех моделей теблиц"""

    repr_cols_num = 10
    repr_cols = tuple()  # type: ignore
    
    id: Mapped[uuidpk]
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        server_default=None,
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:  # type: ignore
                cols.append(f"{col}={getattr(self, col)}")  # type: ignore

        return f"<{self.__class__.__name__} {', '.join(cols)}>"  # type: ignore
