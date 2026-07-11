from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as PgEnum, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, uuid_pk
from .enums import ReviewDecision, ReviewStatus, ScriptureEntityType


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = uuid_pk()
    entity_type: Mapped[ScriptureEntityType] = mapped_column(
        PgEnum(ScriptureEntityType, name="scripture_entity_type"), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    status: Mapped[ReviewStatus] = mapped_column(PgEnum(ReviewStatus, name="review_status"), nullable=False)
    decision: Mapped[ReviewDecision | None] = mapped_column(
        PgEnum(ReviewDecision, name="review_decision"), nullable=True
    )
    reviewer: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_reviews_entity", "entity_type", "entity_id", "created_at"),
    )