from aiomax.bot import Bot
from aiomax.fsm import FSMCursor
from aiomax.types import Callback, CommandContext, Message, PhotoAttachment

from src.bot.flows.auth_flow import handle_auth_message, handle_start, is_auth_state
from src.bot.flows.menu_flow import handle_help, handle_main_menu, handle_settings
from src.bot.flows.objects_flow import handle_new_report_message, handle_object_action, handle_object_details, handle_objects_menu, is_new_report_state
from src.bot.keyboards.callbacks import MenuCallbackPayload, ObjectActionCallbackPayload, ObjectCallbackPayload
from src.messengers.common import IncomingAttachment, IncomingEvent, IncomingEventType
from src.messengers.max.sender import send_max_response
from src.messengers.max.state_adapter import MaxStateStorage


def _event_from_message(message: Message) -> IncomingEvent:
    return IncomingEvent(
        type=IncomingEventType.MESSAGE,
        user_id=message.sender.user_id,
        text=message.content,
        username=message.sender.username,
        attachments=[],
        session_factory=message.bot.session_factory,
        storage_service=message.bot.s3_service,
    )


def _event_from_callback(callback: Callback) -> IncomingEvent:
    return IncomingEvent(
        type=IncomingEventType.CALLBACK,
        user_id=callback.user_id,
        payload=callback.payload,
        session_factory=callback.bot.session_factory,
        storage_service=callback.bot.s3_service,
    )


def _event_from_context(ctx: CommandContext) -> IncomingEvent:
    return IncomingEvent(
        type=IncomingEventType.COMMAND,
        user_id=ctx.sender.user_id,
        username=ctx.sender.username,
        session_factory=ctx.bot.session_factory,
        storage_service=ctx.bot.s3_service,
    )


def _is_auth_message(message: Message) -> bool:
    return is_auth_state(message.bot.storage.get_state(message.sender.user_id))


def _is_new_report_message(message: Message) -> bool:
    return is_new_report_state(message.bot.storage.get_state(message.sender.user_id))


async def _download_photo(bot: Bot, photo: PhotoAttachment) -> IncomingAttachment:
    if bot.session is None:
        raise RuntimeError("Bot HTTP session is not initialized")
    async with bot.session.get(photo.url) as response:
        response.raise_for_status()
        return IncomingAttachment(
            type="photo",
            url=photo.url,
            content=await response.read(),
            content_type=response.headers.get("Content-Type"),
        )


async def _add_photo_attachments(message: Message, event: IncomingEvent) -> None:
    for attachment in message.body.attachments or []:
        if isinstance(attachment, PhotoAttachment) and attachment.url:
            event.attachments.append(await _download_photo(message.bot, attachment))


def setup_max_handlers(bot: Bot) -> None:
    @bot.on_command("start")
    async def start_handler(ctx: CommandContext, cursor: FSMCursor) -> None:
        await send_max_response(ctx, await handle_start(_event_from_context(ctx), MaxStateStorage(cursor)))

    @bot.on_message(_is_auth_message)
    async def auth_message_handler(message: Message, cursor: FSMCursor) -> None:
        await send_max_response(message, await handle_auth_message(_event_from_message(message), MaxStateStorage(cursor)))

    @bot.on_button_callback(MenuCallbackPayload.HELP)
    async def help_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_help(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_button_callback(MenuCallbackPayload.MAIN_MENU)
    async def main_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_main_menu(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_button_callback(MenuCallbackPayload.SETTINGS)
    async def menu_stub_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_settings(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_button_callback(MenuCallbackPayload.OBJECTS)
    async def objects_menu_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_objects_menu(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_button_callback(ObjectCallbackPayload.is_object_callback)
    async def object_details_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_object_details(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_button_callback(ObjectActionCallbackPayload.is_action_callback)
    async def object_action_handler(callback: Callback, cursor: FSMCursor) -> None:
        await send_max_response(callback, await handle_object_action(_event_from_callback(callback), MaxStateStorage(cursor)))

    @bot.on_message(_is_new_report_message)
    async def new_report_message_handler(message: Message, cursor: FSMCursor) -> None:
        event = _event_from_message(message)
        await _add_photo_attachments(message, event)
        await send_max_response(message, await handle_new_report_message(event, MaxStateStorage(cursor)))
