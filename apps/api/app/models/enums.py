from __future__ import annotations

import enum


class NodeType(str, enum.Enum):
    STORY_SLOT = "story_slot"
    BEING = "being"


class ReviewStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"


class ReviewDecision(str, enum.Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ScriptureEntityType(str, enum.Enum):
    NODE = "node"
    EDGE = "edge"


class EmbeddingProvider(str, enum.Enum):
    OPENAI = "openai"
    GEMINI = "gemini"