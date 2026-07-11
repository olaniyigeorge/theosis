from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as PgEnum, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, uuid_pk
from .enums import NodeType, ReviewStatus

if TYPE_CHECKING:
    # only for type checkers — never actually executed, so this doesn't
    # trigger edge.py's import of node.py at runtime.
    from .edge import Edge


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[uuid.UUID] = uuid_pk()
    type: Mapped[NodeType] = mapped_column(PgEnum(NodeType, name="node_type"), nullable=False, index=True)

    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    confidence: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    review_status: Mapped[ReviewStatus] = mapped_column(
        PgEnum(ReviewStatus, name="review_status"), nullable=False, default=ReviewStatus.DRAFT, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationship() takes the class as a STRING here — this is what actually
    # breaks the cycle. SQLAlchemy resolves "Edge" against Base.registry at
    # mapper-configuration time (first query, or explicit configure_mappers()),
    # not when this class body runs. So no real import of edge.py is needed here.
    outgoing_edges: Mapped[list["Edge"]] = relationship(
        foreign_keys="Edge.source_id", back_populates="source", cascade="all, delete-orphan"
    )
    incoming_edges: Mapped[list["Edge"]] = relationship(
        foreign_keys="Edge.target_id", back_populates="target", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_nodes_data_gin", "data", postgresql_using="gin"),
    )