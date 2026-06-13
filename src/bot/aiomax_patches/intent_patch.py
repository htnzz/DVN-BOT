from aiomax.buttons import CallbackButton


def patched_callback_button_from_json(data: dict) -> CallbackButton:
    return CallbackButton(
        text=data["text"],
        payload=data["payload"],
        intent=data.get("intent", "default"),
    )


CallbackButton.from_json = staticmethod(patched_callback_button_from_json)