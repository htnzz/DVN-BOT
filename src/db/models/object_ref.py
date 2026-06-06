import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base
if TYPE_CHECKING:
    from src.db.models.comment import  Comment
    from src.db.models.notification import  Notification
    from src.db.models.audit_log import  AuditLog
    from src.db.models.status_change import  StatusChange


class ObjectRef(Base):
    __tablename__ = "object_refs"
    __table_args__ = (
        Index("ix_object_refs_external_id", "external_id"),
        Index("ix_object_refs_code", "code"),
        Index("ix_object_refs_responsible_external_id", "responsible_external_id"),
        Index("ix_object_refs_start_date", "start_date"),
        Index("ix_object_refs_end_date", "end_date"),
        Index("ix_object_refs_cached_at", "cached_at"),
        Index("ix_object_refs_source_updated_at", "source_updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responsible_external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responsible_id: Mapped[str | None] = mapped_column(String(255), nullable=True) # Переделать в FK для user_id.
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    comments: Mapped[list["Comment"]] = relationship(back_populates="object_ref")
    photo_reports: Mapped[list["PhotoReport"]] = relationship(back_populates="object_ref")
    status_changes: Mapped[list["StatusChange"]] = relationship(back_populates="object_ref")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="object_ref")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="object_ref")
