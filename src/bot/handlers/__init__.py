from aiomax.bot import Bot

from src.bot.handlers.auth import setup_auth_handlers
from src.bot.handlers.menu import setup_menu_handlers
from src.bot.handlers.objects import setup_object_handlers


def setup_handlers(bot: Bot) -> None:
    setup_auth_handlers(bot)
    setup_menu_handlers(bot)
    setup_object_handlers(bot)


__all__ = ("setup_handlers",)
