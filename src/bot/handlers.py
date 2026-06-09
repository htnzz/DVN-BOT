from __future__ import annotations

from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import Callback, CommandContext, Message, PhotoAttachment

from src.bot.keyboards import build_help_keyboard, build_main_menu_keyboard, build_object_details_keyboard, \
    build_objects_keyboard
from src.services import AuthResultStatus, AuthService, MenuCallbackPayload, MenuService, ObjectCallbackPayload, \
    ObjectService

_AUTH_PHONE_STATE = "auth:phone"
_AUTH_PASSWORD_STATE = "auth:password"


def _is_auth_message(message: Message) -> bool:
    return message.bot.storage.get_state(message.sender.user_id) in {
        _AUTH_PHONE_STATE,
        _AUTH_PASSWORD_STATE,
    }


def setup_handlers(bot: Bot) -> None:
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

    @bot.on_button_callback(MenuCallbackPayload.HELP)
    async def help_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        auth_service = AuthService(callback.bot.session_factory)
        user = await auth_service.get_authorized_user(callback.user_id)

        if user is None:
            cursor.clear()
            await callback.answer(
                text="Для доступа к меню авторизуйтесь через /start."
            )
            return

        menu_service = MenuService()
        await callback.answer(
            text=menu_service.get_help_text(),
            keyboard=build_help_keyboard(),
        )

    @bot.on_button_callback(MenuCallbackPayload.MAIN_MENU)
    async def main_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        auth_service = AuthService(callback.bot.session_factory)
        user = await auth_service.get_authorized_user(callback.user_id)

        if user is None:
            cursor.clear()
            await callback.answer(
                text="Для доступа к меню авторизуйтесь через /start."
            )
            return

        menu_service = MenuService()
        await callback.answer(
            text=menu_service.get_main_menu_text(),
            keyboard=build_main_menu_keyboard(),
        )

    @bot.on_button_callback(MenuCallbackPayload.OBJECTS)
    async def objects_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        auth_service = AuthService(callback.bot.session_factory)
        user = await auth_service.get_authorized_user(callback.user_id)

        if user is None:
            cursor.clear()
            await callback.answer(
                text="Для доступа к меню авторизуйтесь через /start."
            )
            return

        object_service = ObjectService(callback.bot.session_factory)
        objects = await object_service.get_user_objects(callback.user_id)
        await callback.answer(
            text=object_service.get_objects_list_text(objects),
            keyboard=build_objects_keyboard(objects),
        )

    @bot.on_button_callback(ObjectCallbackPayload.is_object_callback)
    async def object_details_handler(callback: Callback, cursor: FSMCursor) -> None:
        auth_service = AuthService(callback.bot.session_factory)
        user = await auth_service.get_authorized_user(callback.user_id)

        if user is None:
            cursor.clear()
            await callback.answer(
                text="Для доступа к меню авторизуйтесь через /start."
            )
            return

        object_id = ObjectCallbackPayload.parse(callback.payload)
        if object_id is None:
            await callback.answer(notification="Не удалось определить объект.")
            return

        object_service = ObjectService(callback.bot.session_factory)
        object_details = await object_service.get_user_object_details(
            max_id=callback.user_id,
            object_id=object_id,
        )
        if object_details is None:
            await callback.answer(notification="Объект не найден или недоступен.")
            return

        attachments = (
            PhotoAttachment(url=object_details.photo_url)
            if object_details.photo_url
            else None
        )
        await callback.answer(
            text=object_service.get_object_details_text(object_details),
            keyboard=build_object_details_keyboard(),
            attachments=attachments,
        )

    @bot.on_button_callback(MenuCallbackPayload.SETTINGS)
    async def menu_stub_handler(callback: Callback) -> None:
        menu_service = MenuService()
        await callback.answer(
            notification=menu_service.get_section_in_development_text()
        )

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
