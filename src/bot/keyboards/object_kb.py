from aiomax.buttons import CallbackButton

from src.db.models.object_ref import ObjectRef
from src.services.object_service import ObjectCallbackPayload


def build_objects_keyboard(objects: list[ObjectRef]) -> list[list[CallbackButton]]:
    return [
        [CallbackButton(object_ref.title, ObjectCallbackPayload.build(object_ref.id))]
        for object_ref in objects
    ]


def build_object_details_keyboard() -> list[list[CallbackButton]]:
    return [
        [CallbackButton("📋 Моковая кнопка 1", "mock:object:1", intent="default")],
        [CallbackButton("🛠 Моковая кнопка 2", "mock:object:2", intent="default")],
    ]
    