from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as PgEnum, Index, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, uuid_pk
from .enums import ScriptureEntityType


class ScriptureRef(Base):
    __tablename__ = "scripture_refs"

    id: Mapped[uuid.UUID] = uuid_pk()
    entity_type: Mapped[ScriptureEntityType] = mapped_column(
        PgEnum(ScriptureEntityType, name="scripture_entity_type"), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    book: Mapped[str] = mapped_column(String(30), nullable=False)
    chapter_start: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    verse_start: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    chapter_end: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    verse_end: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    validated: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_scripture_refs_entity", "entity_type", "entity_id"),
        Index("ix_scripture_refs_book_ch_v", "book", "chapter_start", "verse_start"),
        CheckConstraint("chapter_start > 0 AND verse_start > 0", name="ck_scripture_refs_positive"),
    )