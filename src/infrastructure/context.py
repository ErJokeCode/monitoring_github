from contextlib import asynccontextmanager
from contextvars import ContextVar
import logging
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from .database.client_db import ClientDB

_log = logging.getLogger(__name__)

_current_session: ContextVar[AsyncSession] = ContextVar("_current_session")


class StoryContext:
    session_factory = ClientDB.session_factory

    @classmethod
    @asynccontextmanager
    async def begin(cls) -> AsyncIterator[None]:
        """Контекстный менеджер для старта транзакции."""
        async with cls.session_factory() as session:
            async with session.begin():
                # Устанавливаем в контекст
                token = _current_session.set(session)
                try:
                    _log.debug("Start transaction")
                    yield
                    _log.debug("Commit transaction")
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    _log.info("Transaction failed. Rollback transaction")
                    _log.exception(e)
                    raise e
                finally:
                    await session.close()
                    _current_session.reset(token)

    @classmethod
    def get_current_session(cls) -> AsyncSession:
        """Получает текущую сессию из контекста"""
        try:
            return _current_session.get()
        except LookupError:
            raise RuntimeError(
                "No session found. Use within StoryContext.begin() context")
