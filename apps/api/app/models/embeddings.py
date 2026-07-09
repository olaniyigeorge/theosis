from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import HALFVEC, Vector
from sqlalchemy import DateTime, Enum as PgEnum, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, uuid_pk
from .enums import ScriptureEntityType


class EmbeddingMixin:
    id: Mapped[uuid.UUID] = uuid_pk()
    entity_type: Mapped[ScriptureEntityType] = mapped_column(
        PgEnum(ScriptureEntityType, name="scripture_entity_type"), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    model: Mapped[str] = mapped_column(String(60), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_text: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EmbeddingOpenAI(EmbeddingMixin, Base):
    __tablename__ = "embeddings_openai"

    embedding: Mapped[list[float]] = mapped_column(HALFVEC(1536), nullable=False)

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "model", name="uq_embeddings_openai_entity_model"),
        Index(
            "ix_embeddings_openai_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "halfvec_cosine_ops"},
        ),
    )


class EmbeddingGemini(EmbeddingMixin, Base):
    __tablename__ = "embeddings_gemini"

    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=False)

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", "model", name="uq_embeddings_gemini_entity_model"),
        Index(
            "ix_embeddings_gemini_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )