from src.bot.keyboards import build_help_keyboard, build_main_menu_keyboard
from src.messengers.common import BotResponse, IncomingEvent, StateStorage
from src.services import AuthService, MenuService

AUTH_REQUIRED_TEXT = "Для доступа к меню авторизуйтесь через /start."


async def ensure_authorized(event: IncomingEvent, state: StateStorage) -> BotResponse | None:
    user = await AuthService(event.session_factory).get_authorized_user(event.user_id)
    if user is not None:
        return None
    state.clear()
    return BotResponse(text=AUTH_REQUIRED_TEXT)


async def handle_help(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    return BotResponse(text=MenuService().get_help_text(), keyboard=build_help_keyboard())


async def handle_main_menu(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    return BotResponse(text=MenuService().get_main_menu_text(), keyboard=build_main_menu_keyboard())


async def handle_settings(event: IncomingEvent, state: StateStorage) -> BotResponse:
    return BotResponse(notification=MenuService().get_section_in_development_text())
