from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import CommandContext, Message

from src.bot.keyboards import build_main_menu_keyboard
from src.services import AuthResultStatus, AuthService, MenuService

_AUTH_PHONE_STATE = "auth:phone"
_AUTH_PASSWORD_STATE = "auth:password"


def _is_auth_message(message: Message) -> bool:
    return message.bot.storage.get_state(message.sender.user_id) in {
        _AUTH_PHONE_STATE,
        _AUTH_PASSWORD_STATE,
    }


def setup_auth_handlers(bot: Bot) -> None:
    @bot.on_command("start")
    async def start_handler(ctx: CommandContext, cursor: FSMCursor) -> None:
        auth_service = AuthService(ctx.bot.session_factory)
        user = await auth_service.get_authorized_user(ctx.sender.user_id)

        if user is not None:
            cursor.clear()
            menu_service = MenuService()
            await ctx.send(
                menu_service.get_main_menu_text(),
                keyboard=build_main_menu_keyboard(),
            )
            return

        cursor.change_state(_AUTH_PHONE_STATE)
        cursor.change_data({})
        await ctx.send("Здравствуйте! Для авторизации отправьте номер телефона.")

    @bot.on_message(_is_auth_message)
    async def auth_message_handler(message: Message, cursor: FSMCursor) -> None:
        state = cursor.get_state()
        text = (message.content or "").strip()

        if not text:
            await message.send("Пожалуйста, отправьте данные текстовым сообщением.")
            return

        if state == _AUTH_PHONE_STATE:
            cursor.change_data({"phone": text})
            cursor.change_state(_AUTH_PASSWORD_STATE)
            await message.send("Теперь отправьте пароль.")
            return

        if state == _AUTH_PASSWORD_STATE:
            data = cursor.get_data() or {}
            auth_service = AuthService(message.bot.session_factory)
            result = await auth_service.authorize(
                phone=data.get("phone", ""),
                password=text,
                max_id=message.sender.user_id,
                username=message.sender.username,
            )

            if result.status == AuthResultStatus.SUCCESS and result.user is not None:
                cursor.clear()
                await message.send(
                    f"Авторизация успешна. Добро пожаловать!\n"
                    f"Пользователь: {result.user.full_name}.\n"
                    f"Роль: {result.user.role}."
                )
                return

            cursor.clear()
            await message.send(
                "Не удалось авторизоваться: неверный номер телефона или пароль. "
                "Отправьте /start, чтобы попробовать снова."
            )
