from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)

from settings import config


async_engine = create_async_engine(config.postgres_connection_uri, echo=True)

async_session_factory = async_sessionmaker[AsyncSession](bind=async_engine)


async def get_async_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
