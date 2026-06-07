from __future__ import annotations

from aiomax.buttons import CallbackButton

from src.services.menu_service import MenuCallbackPayload


def build_main_menu_keyboard() -> list[list[CallbackButton]]:
    return [
        [CallbackButton("👷‍♂️ Мои объекты", MenuCallbackPayload.OBJECTS)],
        [CallbackButton("⚙️ Настройки", MenuCallbackPayload.SETTINGS)],
        [CallbackButton("❓ Помощь", MenuCallbackPayload.HELP)],
    ]


def build_help_keyboard() -> list[list[CallbackButton]]:
    return [[CallbackButton("◀️ В меню", MenuCallbackPayload.MAIN_MENU)]]
