"""
Single import surface for the ORM layer.

Nothing outside this package should ever do `from app.models.node import Node`.
Always `from app.models import Node`. This guarantees every mapped class is
registered against Base.registry before SQLAlchemy resolves any string-based
relationship() reference (Node <-> Edge) or before Alembic autogenerate walks
Base.metadata — both of which silently miss unregistered classes otherwise.

alembic/env.py should import Base from here:
    from app.models import Base
    target_metadata = Base.metadata
"""
from .base import Base
from .enums import (
    EmbeddingProvider,
    NodeType,
    ReviewDecision,
    ReviewStatus,
    ScriptureEntityType,
)
from .node import Node
from .edge import Edge
from .scripture_ref import ScriptureRef
from .review import Review
from .embeddings import EmbeddingGemini, EmbeddingOpenAI

__all__ = [
    "Base",
    "NodeType",
    "ReviewStatus",
    "ReviewDecision",
    "ScriptureEntityType",
    "EmbeddingProvider",
    "Node",
    "Edge",
    "ScriptureRef",
    "Review",
    "EmbeddingOpenAI",
    "EmbeddingGemini",
]