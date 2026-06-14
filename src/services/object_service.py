from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.db.models.object_ref import ObjectRef
from src.db.uow import UoW


@dataclass(frozen=True, slots=True)
class ObjectDetails:
    title: str
    code: str | None
    photo_url: str | None


class ObjectService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_user_objects(self, max_id: int) -> list[ObjectRef]:
        async with UoW(self._session_factory) as uow:
            user = await uow.users.get_by_messenger_user_id(str(max_id))
            if user is None:
                return []

            return await uow.object_refs.get_by_responsible_id(user.id)

    async def get_user_object_details(
        self,
        *,
        max_id: int,
        object_id: uuid.UUID,
    ) -> ObjectDetails | None:
        async with UoW(self._session_factory) as uow:
            user = await uow.users.get_by_messenger_user_id(str(max_id))
            if user is None:
                return None

            object_ref = await uow.object_refs.get_by_id_and_responsible_id(
                object_id=object_id,
                responsible_id=user.id,
            )
            if object_ref is None:
                return None

            return ObjectDetails(
                title=object_ref.title,
                code=object_ref.code,
                photo_url=object_ref.photo_url,
            )

    @staticmethod
    def get_objects_list_text(objects: list[ObjectRef]) -> str:
        if not objects:
            return "Мои объекты\n\nПока за вами не закреплены объекты."

        return "Мои объекты\n\nВыберите объект из списка ниже."

    @staticmethod
    def get_object_details_text(object_details: ObjectDetails) -> str:
        code = object_details.code or "не указан"
        return (
            "Карточка объекта\n\n"
            f"Название: {object_details.title}\n"
            f"Код: {code}"
        )
