from __future__ import annotations

from pydantic import BaseModel, Field


class ScriptureAdviceRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)


class SuggestedReference(BaseModel):
    """One reference the LLM believes is relevant — not yet verified."""
    book: str
    chapter: int
    verse_start: int
    verse_end: int | None = None
    relevance: str  # why this passage was picked; feeds the second prompt


class SuggestedReferences(BaseModel):
    """Structured output shape for the first (extraction) LLM call."""
    references: list[SuggestedReference]


class ScriptureCitation(BaseModel):
    """A reference that has actually been resolved against the Bible API —
    the only kind allowed into the final advice prompt."""
    book: str
    chapter: int
    verse_start: int
    verse_end: int | None = None
    translation: str
    text: str


class ScriptureAdvice(BaseModel):
    """Structured output shape for the second (composition) LLM call."""
    advice: str


class ScriptureAdviceResponse(BaseModel):
    query: str
    advice: str
    citations: list[ScriptureCitation]