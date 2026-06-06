from src.db.models.status_change import StatusChange
from src.db.repositories.base import BaseRepository


class StatusChangeRepository(BaseRepository[StatusChange]):
    model = StatusChange
