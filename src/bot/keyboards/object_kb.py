from aiomax.buttons import CallbackButton

from src.db.models.object_ref import ObjectRef
from src.bot.keyboards.callbacks import ObjectCallbackPayload, MenuCallbackPayload


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


def build_object_details_keyboard() -> list[list[CallbackButton]]:
    return [
        [CallbackButton("📋 Моковая кнопка 1", "mock:object:1", intent="default")],
        [CallbackButton("🛠 Моковая кнопка 2", "mock:object:2", intent="default")],
    ]
    