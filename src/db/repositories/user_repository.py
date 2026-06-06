from src.db.models.user import User
from src.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User
