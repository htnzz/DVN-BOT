from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.messengers.common.keyboard import Keyboard


class IncomingEventType(StrEnum):
    COMMAND = "command"
    MESSAGE = "message"
    CALLBACK = "callback"


@dataclass(slots=True)
class IncomingAttachment:
    type: str
    url: str | None = None
    content: bytes | None = None
    content_type: str | None = None


@dataclass(slots=True)
class OutgoingAttachment:
    type: str
    file_key: str | None = None
    mime_type: str | None = None
    raw: Any | None = None


@dataclass(slots=True)
class IncomingEvent:
    type: IncomingEventType
    user_id: int
    text: str | None = None
    payload: str | None = None
    username: str | None = None
    attachments: list[IncomingAttachment] = field(default_factory=list)
    session_factory: async_sessionmaker[AsyncSession] | None = None
    storage_service: Any | None = None


@dataclass(slots=True)
class BotResponse:
    text: str | None = None
    notification: str | None = None
    keyboard: Keyboard | None = None
    attachments: list[OutgoingAttachment] = field(default_factory=list)
