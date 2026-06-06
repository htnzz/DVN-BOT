import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import get_settings
from src.db.models import Base

# Важно: импортируем модели, чтобы Alembic увидел их в Base.metadata.
from src.db.models import (  # noqa: F401
AuditLog,
ObjectRef,
User,
Comment,
Notification,
StatusChange
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.postgres_asyncpg_dsn)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций без подключения к БД."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Синхронная часть Alembic внутри async-подключения."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создать async engine и выполнить миграции через asyncpg."""
    section = config.get_section(config.config_ini_section)

    if section is None:
        raise RuntimeError("Alembic config section is missing")

    section["sqlalchemy.url"] = settings.postgres_asyncpg_dsn

    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск online-миграций."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()