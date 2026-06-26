from aiomax.types import Callback

from src.messengers.common import BotResponse
from src.messengers.max.keyboard_adapter import to_max_keyboard


async def send_max_response(target, response: BotResponse) -> None:
    keyboard = to_max_keyboard(response.keyboard)
    attachments = []
    for attachment in response.attachments:
        if attachment.raw is not None:
            attachments.append(attachment.raw)
        elif attachment.type == "image" and attachment.file_key:
            uploaded = await target.bot.max_media_adapter.build_image_attachment_by_file_key(
                bot=target.bot, file_key=attachment.file_key, mime_type=attachment.mime_type
            )
            if uploaded is not None:
                attachments.append(uploaded)

    kwargs = {}
    if response.text is not None:
        kwargs["text"] = response.text
    if response.notification is not None:
        kwargs["notification"] = response.notification
    if keyboard is not None:
        kwargs["keyboard"] = keyboard
    if attachments:
        kwargs["attachments"] = attachments[0] if len(attachments) == 1 else attachments

    if isinstance(target, Callback):
        await target.answer(**kwargs)
    else:
        kwargs.pop("notification", None)
        await target.send(**kwargs)
