from aiomax.buttons import CallbackButton

from src.db.models.object_ref import ObjectRef
from src.bot.keyboards.callbacks import ObjectAction, ObjectActionCallbackPayload, ObjectCallbackPayload, MenuCallbackPayload


def build_objects_keyboard(objects: list[ObjectRef]) -> list[list[CallbackButton]]:
    keyboard: list[list[CallbackButton]] = []

    for object_ref in objects:
        keyboard.append(
            [
                CallbackButton(
                    object_ref.title,
                    ObjectCallbackPayload.build(object_ref.id),
                    intent="default",
                )
            ]
        )

    keyboard.append(
        [
            CallbackButton(
                "◀️ В меню",
                MenuCallbackPayload.MAIN_MENU.value,
                intent="default",
            )
        ]
    )

    return keyboard


def build_object_details_keyboard(object_id) -> list[list[CallbackButton]]:
    return [
        [CallbackButton("📝 Новый отчёт", ObjectActionCallbackPayload.build(ObjectAction.NEW_REPORT, object_id), intent="default")],
        [CallbackButton("📊 Отчёты", ObjectActionCallbackPayload.build(ObjectAction.REPORTS, object_id), intent="default")],
        [CallbackButton("💬 Комментарии", ObjectActionCallbackPayload.build(ObjectAction.COMMENTS, object_id), intent="default")],
        [CallbackButton("📋 К списку объектов", MenuCallbackPayload.OBJECTS.value, intent="default")],
        [CallbackButton("🏠 Главное меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")],

    ]


def build_report_success_keyboard(object_id) -> list[list[CallbackButton]]:
    return [
        [CallbackButton("🏠 Главное меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")],
        [CallbackButton("🏗 К объекту", ObjectCallbackPayload.build(object_id), intent="default")],
    ]


    