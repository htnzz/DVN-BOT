from aiomax.buttons import CallbackButton

from src.messengers.common.keyboard import Keyboard


def to_max_keyboard(keyboard: Keyboard | None) -> list[list[CallbackButton]] | None:
    if keyboard is None:
        return None
    return [[CallbackButton(button.text, button.payload, intent=button.intent) for button in row] for row in keyboard]
