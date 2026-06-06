from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **data: Any) -> ModelType:
        instance = self.model(**data)

        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)

        return instance

    async def get(self, object_id: int) -> ModelType | None:
        return await self.session.get(self.model, object_id)

    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[ModelType]:
        stmt = select(self.model)

        if offset is not None:
            stmt = stmt.offset(offset)

        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.scalars(stmt)
        return list(result.all())

    async def update(self, instance: ModelType, **data: Any) -> ModelType:
        for field, value in data.items():
            if not hasattr(instance, field):
                raise ValueError(f"У модели {self.model.__name__} отсутствует поле {field!r}")
            setattr(instance, field, value)

        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> bool:
        db_instance = await self.get(instance.id)

        if db_instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True
