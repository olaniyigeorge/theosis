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