import uuid

from src.bot.flows.menu_flow import ensure_authorized
from src.bot.keyboards import build_object_details_keyboard, build_objects_keyboard, build_report_success_keyboard
from src.bot.keyboards.callbacks import ObjectAction, ObjectActionCallbackPayload, ObjectCallbackPayload
from src.messengers.common import BotResponse, IncomingEvent, OutgoingAttachment, StateStorage
from src.services import ObjectService, ReportService

NEW_REPORT_STATE = "object:new-report"


def is_new_report_state(state: str | None) -> bool:
    return state == NEW_REPORT_STATE


async def handle_objects_menu(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    object_service = ObjectService(event.session_factory)
    objects = await object_service.get_user_objects(event.user_id)
    return BotResponse(text=object_service.get_objects_list_text(objects), keyboard=build_objects_keyboard(objects))


async def handle_object_details(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    object_id = ObjectCallbackPayload.parse(event.payload)
    if object_id is None:
        return BotResponse(notification="Не удалось определить объект.")
    state.clear()
    return await _build_object_details_response(event, object_id)


async def _build_object_details_response(event: IncomingEvent, object_id: uuid.UUID) -> BotResponse:
    object_service = ObjectService(event.session_factory)
    details = await object_service.get_user_object_details(max_id=event.user_id, object_id=object_id)
    if details is None:
        return BotResponse(notification="Объект не найден или недоступен.")
    attachments = []
    if details.photo_url:
        attachments.append(OutgoingAttachment(type="image", file_key=details.photo_url, mime_type="image/jpeg"))
    return BotResponse(
        text=object_service.get_object_details_text(details),
        keyboard=build_object_details_keyboard(object_id),
        attachments=attachments,
    )


async def handle_object_action(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    parsed = ObjectActionCallbackPayload.parse(event.payload)
    if parsed is None:
        return BotResponse(notification="Не удалось определить действие.")
    action, object_id = parsed
    if action != ObjectAction.NEW_REPORT:
        return BotResponse(notification="Раздел находится в разработке.")
    details = await ObjectService(event.session_factory).get_user_object_details(max_id=event.user_id, object_id=object_id)
    if details is None:
        return BotResponse(notification="Объект не найден или недоступен.")
    state.change_state(NEW_REPORT_STATE)
    state.change_data({"object_id": str(object_id)})
    return BotResponse(text="Отправьте текст отчёта одним сообщением. При необходимости приложите к нему фото.")


async def handle_new_report_message(event: IncomingEvent, state: StateStorage) -> BotResponse:
    denied = await ensure_authorized(event, state)
    if denied:
        return denied
    text = (event.text or "").strip()
    if not text:
        return BotResponse(text="Пожалуйста, отправьте текст отчёта. Фото можно приложить к этому же сообщению.")
    data = state.get_data() or {}
    try:
        object_id = uuid.UUID(data.get("object_id", ""))
    except ValueError:
        state.clear()
        return BotResponse(text="Не удалось определить объект. Откройте карточку объекта и попробуйте снова.")
    photo = next((a for a in event.attachments if a.type == "photo" and a.content), None)
    is_created = await ReportService(event.session_factory, event.storage_service).create_report(
        max_id=event.user_id,
        object_id=object_id,
        text=text,
        image=photo.content if photo else None,
        image_content_type=photo.content_type if photo else None,
    )
    state.clear()
    if not is_created:
        return BotResponse(text="Объект не найден или недоступен.")
    return BotResponse(text="Отчёт успешно отправлен!", keyboard=build_report_success_keyboard(object_id))
