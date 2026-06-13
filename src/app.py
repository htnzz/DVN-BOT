import asyncio
from aiomax.bot import Bot
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

import src.bot.aiomax_patches.intent_patch # noqa: F401
from src.bot import setup_handlers
from src.config.settings import Settings, get_settings
from src.db.session import create_db_engine, create_session_factory


class App:
    def __init__(self, token: str, settings: Settings) -> None:
        self.token = token
        self.settings = settings

        self.db_engine: AsyncEngine = create_db_engine(self.settings.postgres_asyncpg_dsn)
        self.session_factory: async_sessionmaker[AsyncSession] = create_session_factory(
            self.db_engine
        )

        self.bot = Bot(access_token=self.token)

    def _setup_dependencies(self) -> None:
        self.bot.db_engine = self.db_engine
        self.bot.session_factory = self.session_factory

    def _register_bot_components(self) -> None:
        setup_handlers(self.bot)

    async def connect(self) -> None:
        logger.info("Проверяем подключение к базе данных...")

        async with self.db_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        logger.info("Подключение к базе данных успешно проверено")

    async def disconnect(self) -> None:
        logger.info("Закрываем соединения приложения...")

        await self.db_engine.dispose()

        logger.info("Соединения приложения закрыты")

    async def run(self) -> None:
        self._setup_dependencies()
        self._register_bot_components()

        try:
            await self.connect()

            logger.info("Запускаем бота в режиме long polling...")
            await self.bot.start_polling()
        finally:
            await self.disconnect()


async def main() -> None:
    settings = get_settings()
    app = App(token=settings.max_token.get_secret_value(), settings=settings)
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
