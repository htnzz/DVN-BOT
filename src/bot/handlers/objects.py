import uuid

from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import Callback, Message, PhotoAttachment

from src.bot.keyboards import build_object_details_keyboard, build_objects_keyboard, build_report_success_keyboard
from src.bot.keyboards.callbacks import ObjectCallbackPayload, MenuCallbackPayload, ObjectActionCallbackPayload, \
    ObjectAction
from src.services import AuthService, ObjectService, ReportService

_AUTH_REQUIRED_TEXT = "Для доступа к меню авторизуйтесь через /start."
_NEW_REPORT_STATE = "object:new-report"


async def _ensure_authorized(callback: Callback, cursor: FSMCursor) -> bool:
    auth_service = AuthService(callback.bot.session_factory)
    user = await auth_service.get_authorized_user(callback.user_id)

    if user is not None:
        return True

    cursor.clear()
    await callback.answer(text=_AUTH_REQUIRED_TEXT)
    return False


async def _ensure_authorized_message(message: Message, cursor: FSMCursor) -> bool:
    auth_service = AuthService(message.bot.session_factory)
    user = await auth_service.get_authorized_user(message.user_id)

    if user is not None:
        return True

    cursor.clear()
    await message.send(_AUTH_REQUIRED_TEXT)
    return False


def _is_new_report_message(message: Message) -> bool:
    return message.bot.storage.get_state(message.sender.user_id) == _NEW_REPORT_STATE


def _get_photo_attachment(message: Message) -> PhotoAttachment | None:
    for attachment in message.body.attachments or []:
        if isinstance(attachment, PhotoAttachment) and attachment.url:
            return attachment

    return None


async def _download_photo(bot: Bot, photo: PhotoAttachment) -> tuple[bytes, str | None]:
    if bot.session is None:
        raise RuntimeError("Bot HTTP session is not initialized")

    async with bot.session.get(photo.url) as response:
        response.raise_for_status()
        return await response.read(), response.headers.get("Content-Type")


async def _send_object_details(callback: Callback, object_id: uuid.UUID) -> None:
    object_service = ObjectService(callback.bot.session_factory)

    object_details = await object_service.get_user_object_details(
        max_id=callback.user_id,
        object_id=object_id,
    )

    if object_details is None:
        await callback.answer(notification="Объект не найден или недоступен.")
        return

    attachment = None

    if object_details.photo_url:
        attachment = await callback.bot.max_media_service.build_image_attachment_by_file_key(
            bot=callback.bot,
            file_key=object_details.photo_url,
            mime_type="image/jpeg",
        )

    answer_kwargs = {
        "text": object_service.get_object_details_text(object_details),
        "keyboard": build_object_details_keyboard(object_id),
    }

    if attachment is not None:
        answer_kwargs["attachments"] = attachment

    await callback.answer(**answer_kwargs)




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

        cursor.clear()
        await _send_object_details(callback, object_id)

    @bot.on_button_callback(ObjectActionCallbackPayload.is_action_callback)
    async def object_action_handler(callback: Callback, cursor: FSMCursor) -> None:
        if not await _ensure_authorized(callback, cursor):
            return

        parsed_payload = ObjectActionCallbackPayload.parse(callback.payload)
        if parsed_payload is None:
            await callback.answer(notification="Не удалось определить действие.")
            return

        action, object_id = parsed_payload
        if action != ObjectAction.NEW_REPORT:
            await callback.answer(notification="Раздел находится в разработке.")
            return

        object_service = ObjectService(callback.bot.session_factory)

        object_details = await object_service.get_user_object_details(
            max_id=callback.user_id,
            object_id=object_id,
        )

        if object_details is None:
            await callback.answer(notification="Объект не найден или недоступен.")
            return

        cursor.change_state(_NEW_REPORT_STATE)
        cursor.change_data({"object_id": str(object_id)})
        await callback.answer(
            text="Отправьте текст отчёта одним сообщением. При необходимости приложите к нему фото.",
        )

    @bot.on_message(_is_new_report_message)
    async def new_report_message_handler(message: Message, cursor: FSMCursor) -> None:
        if not await _ensure_authorized_message(message, cursor):
            return

        text = (message.content or "").strip()
        if not text:
            await message.send("Пожалуйста, отправьте текст отчёта. Фото можно приложить к этому же сообщению.")
            return

        data = cursor.get_data() or {}
        try:
            object_id = uuid.UUID(data.get("object_id", ""))
        except ValueError:
            cursor.clear()
            await message.send("Не удалось определить объект. Откройте карточку объекта и попробуйте снова.")
            return

        photo = _get_photo_attachment(message)
        image = None
        image_content_type = None
        if photo is not None:
            image, image_content_type = await _download_photo(message.bot, photo)

        report_service = ReportService(message.bot.session_factory, message.bot.s3_service)
        is_created = await report_service.create_report(
            max_id=message.user_id,
            object_id=object_id,
            text=text,
            image=image,
            image_content_type=image_content_type,
        )
        cursor.clear()

        if not is_created:
            await message.send("Объект не найден или недоступен.")
            return

        await message.send(
            "Отчёт успешно отправлен!",
            keyboard=build_report_success_keyboard(object_id),
        )
