"""
Theosis service-layer DTOs — the boundary between the AI draft pipeline /
search endpoints and the ORM. Frozen dataclasses, same pattern as your
semantic-service NormalizedDocument/Chunk/EmbeddedChunk/SearchQuery/SearchResult.

Why this layer exists separately from models.py: the AI provider adapters
(OpenAIEmbeddingAdapter, GeminiEmbeddingAdapter) and the draft pipeline should
never construct or mutate ORM objects directly — they produce these DTOs,
and a repository/service function is the only thing that persists them. Same
separation you already use for GeminiLiveAdapter/OpenAIRealtimeAdapter behind
LiveSessionPort in TrueFit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

EntityKind = Literal["node", "edge"]
EmbeddingProviderName = Literal["openai", "gemini"]


@dataclass(frozen=True)
class ScriptureCitation:
    """
    An unvalidated scripture reference as produced by a draft. Must pass
    through Bible API validation before it becomes a scripture_refs row.
    """
    book: str
    chapter_start: int
    verse_start: int
    chapter_end: int | None = None
    verse_end: int | None = None


@dataclass(frozen=True)
class NodeDraft:
    """
    AI-generated or human-authored draft of a node, pre-persistence.
    Provider-agnostic — same shape regardless of which LLM produced it.
    """
    type: Literal["story_slot", "being"]
    data: dict[str, Any]
    citations: list[ScriptureCitation]
    source_provider: str  # "anthropic" | "gemini" | "openai" | "human"
    confidence: str = "draft"


@dataclass(frozen=True)
class EdgeDraft:
    source_ref: str  # temp key resolved to a node id at persist time, or an existing UUID string
    target_ref: str
    relationship_type: str
    citations: list[ScriptureCitation]
    source_provider: str
    notes: str | None = None
    confidence: str = "draft"


@dataclass(frozen=True)
class EmbeddingResult:
    """
    Pairs an entity with its embedding vector. Kept generic over 
    entity_kind so both nodes and edges (via their derived text) 
    can flow through the same embedding service.
    """
    entity_type: EntityKind
    entity_id: UUID
    provider: EmbeddingProviderName
    model: str
    source_text: str
    vector: list[float]
    model_version: str | None = None


@dataclass(frozen=True)
class SemanticSearchQuery:
    query: str
    top_k: int = 10
    min_score: float | None = None
    node_type: Literal["story_slot", "being"] | None = None
    provider: EmbeddingProviderName = "openai"
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SemanticSearchResult:
    entity_type: EntityKind
    entity_id: UUID
    score: float
    data: dict[str, Any]
    provider: EmbeddingProviderName


@dataclass(frozen=True)
class ReviewDecisionInput:
    entity_type: EntityKind
    entity_id: UUID
    decision: Literal["approved", "rejected", "revision_requested"]
    reviewer: str
    notes: str | None = None