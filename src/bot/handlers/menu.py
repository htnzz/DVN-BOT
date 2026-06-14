from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import Callback

from src.bot.keyboards import build_help_keyboard, build_main_menu_keyboard
from src.services import AuthService, MenuService
from src.bot.keyboards.callbacks import MenuCallbackPayload

_AUTH_REQUIRED_TEXT = "Для доступа к меню авторизуйтесь через /start."


async def _ensure_authorized(callback: Callback, cursor: FSMCursor) -> bool:
    auth_service = AuthService(callback.bot.session_factory)
    user = await auth_service.get_authorized_user(callback.user_id)

    if user is not None:
        return True

    cursor.clear()
    await callback.answer(text=_AUTH_REQUIRED_TEXT)
    return False


def setup_menu_handlers(bot: Bot) -> None:
    @bot.on_button_callback(MenuCallbackPayload.HELP)
    async def help_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        if not await _ensure_authorized(callback, cursor):
            return

        menu_service = MenuService()
        await callback.answer(
            text=menu_service.get_help_text(),
            keyboard=build_help_keyboard(),
        )

    @bot.on_button_callback(MenuCallbackPayload.MAIN_MENU)
    async def main_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        if not await _ensure_authorized(callback, cursor):
            return

        menu_service = MenuService()
        await callback.answer(
            text=menu_service.get_main_menu_text(),
            keyboard=build_main_menu_keyboard(),
        )

    @bot.on_button_callback(MenuCallbackPayload.SETTINGS)
    async def menu_stub_handler(callback: Callback) -> None:
        menu_service = MenuService()
        await callback.answer(
            notification=menu_service.get_section_in_development_text()
        )