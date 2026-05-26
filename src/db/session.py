from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_db_engine(db_url: str) -> AsyncEngine:
    return create_async_engine(
        url=db_url,
        pool_size=5,
        max_overflow=3,
        pool_timeout=15,
        pool_recycle=1800,
        pool_pre_ping=True,
        pool_use_lifo=True,
        connect_args={
            "statement_cache_size": 0,
            "command_timeout": 5.0,
            "server_settings": {"timezone": "UTC"},
        },
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
