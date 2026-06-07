from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models.user import User
from src.db.uow import UoW
from src.integrations.gis_mock import authenticate_user


def normalize_phone(phone: str) -> str:
    normalized_phone = phone.strip()

    if (
        len(normalized_phone) == 11
        and normalized_phone.startswith("8")
        and normalized_phone.isdigit()
    ):
        return f"+7{normalized_phone[1:]}"

    return normalized_phone


class AuthResultStatus(StrEnum):
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"


@dataclass(frozen=True, slots=True)
class AuthResult:
    status: AuthResultStatus
    user: User | None = None


class AuthService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_authorized_user(self, max_id: int) -> User | None:
        async with UoW(self._session_factory) as uow:
            return await uow.users.get_by_messenger_user_id(str(max_id))

    async def authorize(
        self,
        *,
        phone: str,
        password: str,
        max_id: int,
        username: str | None,
    ) -> AuthResult:
        normalized_phone = normalize_phone(phone)
        gis_user = await authenticate_user(phone=normalized_phone, password=password)
        if gis_user is None:
            return AuthResult(status=AuthResultStatus.INVALID_CREDENTIALS)

        async with UoW(self._session_factory) as uow:
            user = await uow.users.get_by_gis_user_id(gis_user.id)
            if user is None:
                user = await uow.users.get_by_phone(gis_user.phone)
            if user is None:
                user = await uow.users.get_by_messenger_user_id(str(max_id))

            user_data = {
                "gis_user_id": gis_user.id,
                "messenger_user_id": str(max_id),
                "username": username,
                "phone": gis_user.phone,
                "full_name": gis_user.full_name,
                "role": gis_user.role,
            }

            if user is None:
                user = await uow.users.create(**user_data)
            else:
                user = await uow.users.update(user, **user_data)

            return AuthResult(status=AuthResultStatus.SUCCESS, user=user)
