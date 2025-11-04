import orjson
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from settings import config


def build_sa_engine() -> AsyncEngine:
    """Создает SQLAlchemy async engine."""
    engine = create_async_engine(
        config.postgres_connection_uri,
        echo=True,
        echo_pool=True,
        json_serializer=lambda data: orjson.dumps(data).decode(),
        json_deserializer=orjson.loads,
        pool_size=50,
    )
    return engine


def build_sa_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    return session_factory
