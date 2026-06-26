from __future__ import annotations

from src.messengers.common.keyboard import Button, Keyboard

from src.bot.keyboards.callbacks import MenuCallbackPayload


def build_main_menu_keyboard() -> Keyboard:
    return [
        [Button("👷‍♂️ Мои объекты", MenuCallbackPayload.OBJECTS.value, intent="default")],
        [Button("⚙️ Настройки", MenuCallbackPayload.SETTINGS.value, intent="positive")],
        [Button("❓ Помощь", MenuCallbackPayload.HELP.value, intent="negative")],
    ]


def build_help_keyboard() -> Keyboard:
    return [[Button("◀️ В меню", MenuCallbackPayload.MAIN_MENU.value, intent="default")]]
