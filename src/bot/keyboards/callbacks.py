import uuid
from enum import StrEnum


_OBJECT_CALLBACK_PREFIX = "object:"
_OBJECT_ACTION_CALLBACK_PREFIX = "object-action:"


class MenuCallbackPayload(StrEnum):
    OBJECTS = "menu:objects"
    SETTINGS = "menu:settings"
    HELP = "menu:help"
    MAIN_MENU = "menu:main"


class ObjectAction(StrEnum):
    NEW_REPORT = "new-report"
    REPORTS = "reports"
    COMMENTS = "comments"


class ObjectCallbackPayload:
    @staticmethod
    def build(object_id: uuid.UUID) -> str:
        return f"{_OBJECT_CALLBACK_PREFIX}{object_id}"

    @staticmethod
    def is_object_callback(callback_or_payload: object) -> bool:
        payload = getattr(callback_or_payload, "payload", callback_or_payload)
        return isinstance(payload, str) and payload.startswith(_OBJECT_CALLBACK_PREFIX)

    @staticmethod
    def parse(payload: str | None) -> uuid.UUID | None:
        if not ObjectCallbackPayload.is_object_callback(payload):
            return None

        raw_object_id = payload.removeprefix(_OBJECT_CALLBACK_PREFIX)
        try:
            return uuid.UUID(raw_object_id)
        except ValueError:
            return None


class ObjectActionCallbackPayload:
    @staticmethod
    def build(action: ObjectAction, object_id: uuid.UUID) -> str:
        return f"{_OBJECT_ACTION_CALLBACK_PREFIX}{action.value}:{object_id}"

    @staticmethod
    def is_action_callback(callback_or_payload: object) -> bool:
        payload = getattr(callback_or_payload, "payload", callback_or_payload)
        return isinstance(payload, str) and payload.startswith(_OBJECT_ACTION_CALLBACK_PREFIX)

    @staticmethod
    def parse(payload: str | None) -> tuple[ObjectAction, uuid.UUID] | None:
        if not ObjectActionCallbackPayload.is_action_callback(payload):
            return None

        raw_payload = payload.removeprefix(_OBJECT_ACTION_CALLBACK_PREFIX)
        raw_action, separator, raw_object_id = raw_payload.partition(":")
        if not separator:
            return None

        try:
            return ObjectAction(raw_action), uuid.UUID(raw_object_id)
        except ValueError:
            return None