from src.bot.keyboards import build_main_menu_keyboard
from src.messengers.common import BotResponse, IncomingEvent, StateStorage
from src.services import AuthResultStatus, AuthService, MenuService

AUTH_PHONE_STATE = "auth:phone"
AUTH_PASSWORD_STATE = "auth:password"


def is_auth_state(state: str | None) -> bool:
    return state in {AUTH_PHONE_STATE, AUTH_PASSWORD_STATE}


async def handle_start(event: IncomingEvent, state: StateStorage) -> BotResponse:
    auth_service = AuthService(event.session_factory)
    user = await auth_service.get_authorized_user(event.user_id)
    if user is not None:
        state.clear()
        return BotResponse(text=MenuService().get_main_menu_text(), keyboard=build_main_menu_keyboard())
    state.change_state(AUTH_PHONE_STATE)
    state.change_data({})
    return BotResponse(text="Здравствуйте! Для авторизации отправьте номер телефона.")


async def handle_auth_message(event: IncomingEvent, state: StateStorage) -> BotResponse:
    current_state = state.get_state()
    text = (event.text or "").strip()
    if not text:
        return BotResponse(text="Пожалуйста, отправьте данные текстовым сообщением.")
    if current_state == AUTH_PHONE_STATE:
        state.change_data({"phone": text})
        state.change_state(AUTH_PASSWORD_STATE)
        return BotResponse(text="Теперь отправьте пароль.")
    if current_state == AUTH_PASSWORD_STATE:
        data = state.get_data() or {}
        result = await AuthService(event.session_factory).authorize(
            phone=data.get("phone", ""), password=text, max_id=event.user_id, username=event.username
        )
        state.clear()
        if result.status == AuthResultStatus.SUCCESS and result.user is not None:
            return BotResponse(text=(
                f"Авторизация успешна. Добро пожаловать!\n"
                f"Пользователь: {result.user.full_name}.\n"
                f"Роль: {result.user.role}."
            ))
        return BotResponse(text=(
            "Не удалось авторизоваться: неверный номер телефона или пароль. "
            "Отправьте /start, чтобы попробовать снова."
        ))
    return BotResponse(text="Отправьте /start, чтобы начать авторизацию.")
