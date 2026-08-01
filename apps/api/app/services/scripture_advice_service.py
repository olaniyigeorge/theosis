from __future__ import annotations

import logging

from pydantic import ValidationError

from app.llm.base import LLMProvider
from app.llm.registry import get_llm_provider  # ASSUMPTION — same import ai_drafts.py uses
from app.schemas.scripture_advice import (
    ScriptureAdvice,
    ScriptureAdviceResponse,
    ScriptureCitation,
    SuggestedReference,
    SuggestedReferences,
)
from app.services.bible_provider import BibleProvider, get_bible_provider
from app.shared.exceptions import (
    BibleAPIUnavailableError,
    BibleRateLimitedError,
    BibleReferenceNotFoundError,
    LLMGenerationError,
)

logger = logging.getLogger(__name__)

MAX_REFERENCES = 5


class ScriptureAdviceGenerationError(Exception):
    """LLM call failed, or every suggested reference failed Bible API validation."""


def _to_reference_string(ref: SuggestedReference) -> str:
    """Builds the human-reference string BibleProvider.get_passage() expects,
    e.g. 'john 3:16-18'."""
    if ref.verse_end and ref.verse_end != ref.verse_start:
        return f"{ref.book} {ref.chapter}:{ref.verse_start}-{ref.verse_end}"
    return f"{ref.book} {ref.chapter}:{ref.verse_start}"


class ScriptureAdviceService:
    def __init__(self, bible_provider: BibleProvider | None = None) -> None:
        self.bible_provider = bible_provider or get_bible_provider()

    async def get_advice(self, query: str) -> ScriptureAdviceResponse:
        llm = get_llm_provider()

        suggestions = await self._suggest_references(llm, query)
        citations = await self._verify_references(suggestions.references)

        if not citations:
            raise ScriptureAdviceGenerationError(
                "None of the suggested scripture references could be verified"
            )

        advice = await self._compose_advice(llm, query, citations)

        return ScriptureAdviceResponse(
            query=query, advice=advice.advice, citations=citations
        )

    async def _suggest_references(self, llm: LLMProvider, query: str) -> SuggestedReferences:
        system_prompt = (
            "You are a biblical counseling assistant. Given a person's real-life "
            "question, identify the underlying theme or need, then suggest up to "
            f"{MAX_REFERENCES} specific Bible passages (book, chapter, and verse "
            "range) that speak to it. Use exact, real references you are "
            "confident exist — every reference will be independently checked "
            "against a Bible API, so do not invent chapter or verse numbers. "
            "For each, give a one-sentence reason it's relevant to the question."
        )
        try:
            raw = await llm.generate_structured(
                system_prompt=system_prompt,
                user_prompt=query,
                response_model=SuggestedReferences,
            )
            print("LLM raw suggested references:", raw)
        except LLMGenerationError as error:
            raise ScriptureAdviceGenerationError(
                f"Could not extract intent from query: {error}"
            ) from error

        try:
            return SuggestedReferences.model_validate(raw)
        except ValidationError as error:
            raise ScriptureAdviceGenerationError(
                f"LLM reference suggestions failed validation: {error}"
            ) from error

    async def _verify_references(
        self, suggestions: list[SuggestedReference]
    ) -> list[ScriptureCitation]:
        citations: list[ScriptureCitation] = []

        for ref in suggestions[:MAX_REFERENCES]:
            reference_str = _to_reference_string(ref)
            try:
                passage = await self.bible_provider.get_passage(reference_str)
            except BibleReferenceNotFoundError:
                # LLM hallucinated a reference that doesn't exist — drop it
                # rather than failing the whole request over one bad citation.
                logger.info("Dropping unverifiable scripture reference: %s", reference_str)
                continue
            except (BibleAPIUnavailableError, BibleRateLimitedError):
                logger.warning("Bible API unavailable for reference: %s", reference_str)
                continue

            citations.append(
                ScriptureCitation(
                    book=ref.book,
                    chapter=ref.chapter,
                    verse_start=ref.verse_start,
                    verse_end=ref.verse_end,
                    translation=passage.translation_name,
                    text=passage.text.strip(),
                )
            )

        return citations

    async def _compose_advice(
        self, llm: LLMProvider, query: str, citations: list[ScriptureCitation]
    ) -> ScriptureAdvice:
        passages_block = "\n\n".join(
            f"{c.book} {c.chapter}:{c.verse_start}"
            f"{f'-{c.verse_end}' if c.verse_end else ''} ({c.translation}): {c.text}"
            for c in citations
        )

        system_prompt = (
            "You are a biblical counseling assistant. You will be given a "
            "person's question and a set of scripture passages that have "
            "already been verified as real and accurate. Write warm, practical "
            "advice grounded ONLY in the passages provided — do not introduce "
            "any scripture reference that isn't in the list below. Reference "
            "the passages by book, chapter, and verse as you draw on them."
            "The response should be valid JSON in the specified format."
        )
        user_prompt = f"Question: {query}\n\nVerified passages:\n{passages_block}"

        try:
            raw = await llm.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=ScriptureAdvice,
            )
        except LLMGenerationError as error:
            raise ScriptureAdviceGenerationError(
                f"Could not compose advice: {error}"
            ) from error

        try:
            return ScriptureAdvice.model_validate(raw)
        except ValidationError as error:
            raise ScriptureAdviceGenerationError(
                f"LLM advice output failed validation: {error}"
            ) from error