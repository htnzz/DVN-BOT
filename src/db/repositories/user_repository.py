from sqlalchemy import select

from src.db.models.user import User
from src.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_messenger_user_id(self, messenger_user_id: str) -> User | None:
        stmt = select(User).where(User.messenger_user_id == messenger_user_id)
        return await self.session.scalar(stmt)

    async def get_by_gis_user_id(self, gis_user_id: int) -> User | None:
        stmt = select(User).where(User.gis_user_id == gis_user_id)
        return await self.session.scalar(stmt)

    async def get_by_phone(self, phone: str) -> User | None:
        stmt = select(User).where(User.phone == phone)
        return await self.session.scalar(stmt)
