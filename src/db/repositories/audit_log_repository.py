from src.db.models.audit_log import AuditLog
from src.db.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
