from __future__ import annotations

from src.bot.keyboards.callbacks import MenuCallbackPayload, ObjectAction, ObjectActionCallbackPayload, ObjectCallbackPayload
from src.db.models.object_ref import ObjectRef
from src.messengers.common.keyboard import Button, Keyboard


def build_objects_keyboard(objects: list[ObjectRef]) -> Keyboard:
    keyboard: Keyboard = []

    for object_ref in objects:
        keyboard.append([Button(object_ref.title, ObjectCallbackPayload.build(object_ref.id), intent="default")])
    keyboard.append([Button("◀️ В меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")])
    return keyboard


def build_object_details_keyboard(object_id) -> Keyboard:
    return [
        [Button("📝 Новый отчёт", ObjectActionCallbackPayload.build(ObjectAction.NEW_REPORT, object_id), intent="default")],
        [Button("📊 Отчёты", ObjectActionCallbackPayload.build(ObjectAction.REPORTS, object_id), intent="default")],
        [Button("💬 Комментарии", ObjectActionCallbackPayload.build(ObjectAction.COMMENTS, object_id), intent="default")],
        [Button("📋 К списку объектов", MenuCallbackPayload.OBJECTS.value, intent="default")],
        [Button("🏠 Главное меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")],
    ]


def build_report_success_keyboard(object_id) -> Keyboard:
    return [
        [Button("🏠 Главное меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")],
        [Button("🏗 К объекту", ObjectCallbackPayload.build(object_id), intent="default")],
    ]