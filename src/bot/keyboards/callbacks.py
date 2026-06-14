import uuid
from dataclasses import dataclass
from enum import StrEnum


_OBJECT_CALLBACK_PREFIX = "object:"


class MenuCallbackPayload(StrEnum):
    OBJECTS = "menu:objects"
    SETTINGS = "menu:settings"
    HELP = "menu:help"
    MAIN_MENU = "menu:main"

class ObjectCallbackPayload:
    @staticmethod
    def build(object_id: uuid.UUID) -> str:
        return f"{_OBJECT_CALLBACK_PREFIX}{object_id}"

    @staticmethod
    def is_object_callback(callback_or_payload: object) -> bool:
        payload = getattr(callback_or_payload, "payload", callback_or_payload)
        return (
            isinstance(payload, str)
            and payload.startswith(_OBJECT_CALLBACK_PREFIX)
        )

    @staticmethod
    def parse(payload: str | None) -> uuid.UUID | None:
        if not ObjectCallbackPayload.is_object_callback(payload):
            return None

        raw_object_id = payload.removeprefix(_OBJECT_CALLBACK_PREFIX)
        try:
            return uuid.UUID(raw_object_id)
        except ValueError:
            return None
