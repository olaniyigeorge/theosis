from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum as PgEnum, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, uuid_pk
from .enums import ReviewStatus

if TYPE_CHECKING:
    from .node import Node


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[uuid.UUID] = uuid_pk()
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)

    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    review_status: Mapped[ReviewStatus] = mapped_column(
        PgEnum(ReviewStatus, name="review_status"), nullable=False, default=ReviewStatus.DRAFT, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped["Node"] = relationship(foreign_keys=[source_id], back_populates="outgoing_edges")
    target: Mapped["Node"] = relationship(foreign_keys=[target_id], back_populates="incoming_edges")

    __table_args__ = (
        CheckConstraint("source_id != target_id", name="ck_edges_no_self_loop"),
        Index("ix_edges_source_target", "source_id", "target_id"),
    )