import uuid

from sqlalchemy import select

from src.db.models.object_ref import ObjectRef
from src.db.repositories.base import BaseRepository


class ObjectRefRepository(BaseRepository[ObjectRef]):
    model = ObjectRef

    async def get_by_responsible_id(self, responsible_id: uuid.UUID) -> list[ObjectRef]:
        stmt = (
            select(ObjectRef)
            .where(ObjectRef.responsible_id == responsible_id)
            .order_by(ObjectRef.title)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_by_id_and_responsible_id(
            self,
            *,
            object_id: uuid.UUID,
            responsible_id: uuid.UUID,
    ) -> ObjectRef | None:
        stmt = select(ObjectRef).where(
            ObjectRef.id == object_id,
            ObjectRef.responsible_id == responsible_id,
        )
        return await self.session.scalar(stmt)
