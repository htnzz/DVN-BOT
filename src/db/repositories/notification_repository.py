from src.db.models.notification import Notification
from src.db.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    model = Notification
