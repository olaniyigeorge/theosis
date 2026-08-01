from __future__ import annotations

from functools import lru_cache

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import settings
from app.shared.exceptions import (
    BibleAPIUnavailableError,
    BibleRateLimitedError,
    BibleReferenceNotFoundError,
)
from app.schemas.scripture import BibleChapter, BiblePassage, BibleRandomVerse

# bible-api.com is rate limited to 15 requests / 30s per IP (stated in their
# docs, not enforced client-side by them beyond a 429). Retry only on 429,
# with backoff, rather than failing the caller on the first rate-limit hit.
_retry_on_rate_limit = retry(
    retry=retry_if_exception_type(BibleRateLimitedError),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    stop=stop_after_attempt(4),
    reraise=True,
)


def _raise_for_status(response: httpx.Response, *, reference: str) -> None:
    if response.status_code == 404:
        raise BibleReferenceNotFoundError(reference)
    if response.status_code == 429:
        raise BibleRateLimitedError(reference)
    response.raise_for_status()


class BibleProvider:
    """Async client for https://bible-api.com/.

    Two endpoint families on the upstream API:
      - reference lookup:  GET /{book chapter:verse}?translation=xx
      - data lookup:       GET /data/{translation}/{book_id}/{chapter}
                           GET /data/{translation}/random[/{book_ids}]
    """

    def __init__(
        self,
        base_url: str | None = None,
        default_translation: str = "web",
        timeout: float = 10.0,
    ):
        self.base_url = (base_url or settings.BIBLE_API_BASE_URL).rstrip("/")
        self.default_translation = default_translation
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BibleProvider":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.aclose()

    @_retry_on_rate_limit
    async def get_passage(self, reference: str, translation: str | None = None) -> BiblePassage:
        """Look up a verse or passage by human reference,
        e.g. 'john 3:16' or 'matt 25:31-33,46'."""
        params = {"translation": translation or self.default_translation}
        try:
            response = await self._client.get(f"/{reference}", params=params)
        except httpx.RequestError as exc:
            raise BibleAPIUnavailableError(str(exc)) from exc
        _raise_for_status(response, reference=reference)
        return BiblePassage.model_validate(response.json())

    @_retry_on_rate_limit
    async def get_chapter(
        self, book_id: str, chapter: int, translation: str | None = None
    ) -> BibleChapter:
        """Fetch every verse in a chapter, e.g. book_id='JHN', chapter=3."""
        translation = translation or self.default_translation
        try:
            response = await self._client.get(f"/data/{translation}/{book_id.upper()}/{chapter}")
        except httpx.RequestError as exc:
            raise BibleAPIUnavailableError(str(exc)) from exc
        _raise_for_status(response, reference=f"{book_id} {chapter}")
        return BibleChapter.model_validate(response.json())

    @_retry_on_rate_limit
    async def get_random_verse(
        self, translation: str | None = None, book_ids: str | None = None
    ) -> BibleRandomVerse:
        """Random verse. book_ids is a comma-separated list of book IDs
        (e.g. 'MAT,MRK,LUK,JHN'), or the special strings 'OT' / 'NT'."""
        translation = translation or self.default_translation
        path = f"/data/{translation}/random"
        if book_ids:
            path = f"{path}/{book_ids}"
        try:
            response = await self._client.get(path)
        except httpx.RequestError as exc:
            raise BibleAPIUnavailableError(str(exc)) from exc
        _raise_for_status(response, reference=book_ids or "random")
        return BibleRandomVerse.model_validate(response.json())


@lru_cache
def get_bible_provider() -> BibleProvider:
    """FastAPI dependency — one shared BibleProvider (and its underlying
    httpx connection pool) per process.

    NOTE: this doesn't close the underlying httpx.AsyncClient anywhere.
    You'll want to call `get_bible_provider().aclose()` in a FastAPI
    shutdown event in main.py, the same way you'd close a DB pool —
    I don't have main.py's content, so I haven't wired that up.
    """
    return BibleProvider()


if __name__ == "__main__":
    # Manual smoke test — hits the real bible-api.com. Run with:
    #   python -m app.services.bible_provider
    # from apps/api (no ".py" suffix on the module path, and not
    # `python app/services/bible_provider.py` — that path form never puts
    # `app/` on sys.path and `from app.shared...` will fail).
    #
    # Guarded behind __name__ == "__main__" deliberately: this module gets
    # imported by other services (e.g. node_service.py) -> imported by the
    # app on every boot, so any module-level code here (not inside this
    # block) — including a bare top-level `await`, which is a SyntaxError
    # outside async def anyway — would run/fail on every startup.
    import asyncio

    async def _main() -> None:
        provider = get_bible_provider()
        try:
            print("\n--- get_passage: single verse ---\n")
            verse = await provider.get_passage("john 3:16")
            print(verse)

            print("\n--- get_passage: verse range ---\n")
            passage = await provider.get_passage("john 3:16-18")
            print(passage)

            print("\n--- get_passage: whole chapter via reference lookup ---\n")
            # get_passage takes any reference string bible-api.com accepts —
            # a bare "john 3" (no verse) returns the whole chapter through
            # the *reference* endpoint, which is a different response shape
            # (BiblePassage: reference/verses/text) than get_chapter below
            # (BibleChapter: translation/verses) even though both return
            # "all of John 3" — they're two different upstream endpoints.
            chapter_via_reference = await provider.get_passage("john 3")
            print(f"{len(chapter_via_reference.verses)} verses")

            print("\n--- get_passage: different translation ---\n")
            kjv_verse = await provider.get_passage("john 3:16", translation="kjv")
            print(kjv_verse.translation_name)

            print("\n--- get_chapter: same chapter via the /data endpoint ---\n")
            chapter = await provider.get_chapter("jhn", 3)
            print(f"{len(chapter.verses)} verses, translation={chapter.translation.identifier}")

            print("\n--- get_random_verse: unscoped ---\n")
            rand_verse = await provider.get_random_verse()
            print(rand_verse)

            print("\n--- get_random_verse: scoped to the Gospels ---\n")
            rand_gospel_verse = await provider.get_random_verse(book_ids="MAT,MRK,LUK,JHN")
            print(rand_gospel_verse)

            print("\n--- get_random_verse: scoped to OT/NT shorthand ---\n")
            rand_nt_verse = await provider.get_random_verse(book_ids="NT")
            print(rand_nt_verse)
        finally:
            await provider.aclose()

    asyncio.run(_main())