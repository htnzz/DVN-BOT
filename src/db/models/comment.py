import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Text, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models import Base, User, ObjectRef
from src.enums import ObjectCommentType

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index("ix_comments_object_ref_id", "object_ref_id"),
        Index("ix_comments_author_id", "author_id"),
        Index("ix_comments_created_at", "created_at"),
        Index("ix_comments_deleted_at", "deleted_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    object_ref_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("object_refs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    comment_type: Mapped[ObjectCommentType] = mapped_column(
        SQLEnum(
            ObjectCommentType,
            name="object_comment_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=ObjectCommentType.COMMENT,
        server_default=ObjectCommentType.COMMENT.value,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    attachments: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    object_ref: Mapped["ObjectRef"] = relationship(
        back_populates="comments",
    )

    author: Mapped["User"] = relationship(
        back_populates="object_comments",
    )