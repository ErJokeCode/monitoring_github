from .base_model import Base
from config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class ClientDB:
    async_url = settings.DATABASE_URL_asyncpg

    engine = create_async_engine(async_url)
    session_factory = async_sessionmaker(engine)

    @classmethod
    async def init_db(cls):
        """Инициализация БД """
        async with cls.engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(
                    sync_conn, checkfirst=True)
            )
