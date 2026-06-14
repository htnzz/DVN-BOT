from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import Callback, PhotoAttachment

from src.bot.keyboards import build_object_details_keyboard, build_objects_keyboard
from src.services import AuthService, ObjectService
from src.bot.keyboards.callbacks import ObjectCallbackPayload, MenuCallbackPayload

_AUTH_REQUIRED_TEXT = "Для доступа к меню авторизуйтесь через /start."


async def _ensure_authorized(callback: Callback, cursor: FSMCursor) -> bool:
    auth_service = AuthService(callback.bot.session_factory)
    user = await auth_service.get_authorized_user(callback.user_id)

    if user is not None:
        return True

    cursor.clear()
    await callback.answer(text=_AUTH_REQUIRED_TEXT)
    return False


def setup_object_handlers(bot: Bot) -> None:
    @bot.on_button_callback(MenuCallbackPayload.OBJECTS)
    async def objects_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        if not await _ensure_authorized(callback, cursor):
            return

        object_service = ObjectService(callback.bot.session_factory)
        objects = await object_service.get_user_objects(callback.user_id)
        await callback.answer(
            text=object_service.get_objects_list_text(objects),
            keyboard=build_objects_keyboard(objects),
        )

    @bot.on_button_callback(ObjectCallbackPayload.is_object_callback)
    async def object_details_handler(callback: Callback, cursor: FSMCursor) -> None:
        if not await _ensure_authorized(callback, cursor):
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
