import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base
if TYPE_CHECKING:
    from src.db.models.object_ref import  ObjectRef
    from src.db.models.user import User


class StatusChange(Base):
    __tablename__ = "status_changes"
    __table_args__ = (
        Index("ix_status_changes_object_ref_id", "object_ref_id"),
        Index("ix_status_changes_author_id", "author_id"),
        Index("ix_status_changes_confirmation_status", "confirmation_status"),
        Index("ix_status_changes_confirmed_by_id", "confirmed_by_id"),
        Index("ix_status_changes_confirmed_at", "confirmed_at"),
        Index("ix_status_changes_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_ref_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("object_refs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    old_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    new_status: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmation_status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending", server_default="pending")
    confirmed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    object_ref: Mapped["ObjectRef"] = relationship(back_populates="status_changes")
    author: Mapped["User"] = relationship(back_populates="status_changes", foreign_keys=[author_id])
    confirmed_by: Mapped["User"] = relationship(back_populates="confirmed_status_changes", foreign_keys=[confirmed_by_id])
