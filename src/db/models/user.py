import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base
if TYPE_CHECKING:
    from src.db.models.comment import  Comment
    from src.db.models.audit_log import  AuditLog
    from src.db.models.status_change import  StatusChange
    from src.db.models.notification import  Notification
    from src.db.models.object_ref import ObjectRef


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_messenger_user_id", "messenger_user_id"),
        Index("ix_users_phone", "phone"),
        Index("ix_users_role", "role"),
        Index("ix_users_gis_user_id", "gis_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    messenger_user_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    gis_user_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
    objects: Mapped[list["ObjectRef"]] = relationship(back_populates="responsible")
    status_changes: Mapped[list["StatusChange"]] = relationship(
        back_populates="author",
        foreign_keys="StatusChange.author_id",
    )
    confirmed_status_changes: Mapped[list["StatusChange"]] = relationship(
        back_populates="confirmed_by",
        foreign_keys="StatusChange.confirmed_by_id",
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="recipient")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")
