import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base
if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.audit_log import  AuditLog


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_audit_log_recipients_audit_log_id", "audit_log_id"),
        Index("ix_audit_log_recipients_recipient_id", "recipient_id"),
        Index("ix_audit_log_recipients_sent_at", "sent_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    audit_log_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_logs.id", ondelete="CASCADE"),
        nullable=False,
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    audit_log: Mapped["AuditLog"] = relationship(
        back_populates="recipients",
    )

    recipient: Mapped["User"] = relationship(
        back_populates="audit_log_recipients",
    )