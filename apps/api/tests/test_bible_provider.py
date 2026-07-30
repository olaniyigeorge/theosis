"""
Tests for BibleProvider. All HTTP calls are mocked via respx — nothing here
hits the real bible-api.com. Fixture payloads are copied verbatim from live
responses captured 2026-07-29 (john 3:16 / data/web/JHN/3 / data/web/random),
so they reflect the real (inconsistent) field names, not a guess.

Requires: pip install pytest pytest-asyncio respx
"""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio
import respx

from app.services.bible_provider import BibleProvider
from app.shared.exceptions import (
    BibleAPIUnavailableError,
    BibleRateLimitedError,
    BibleReferenceNotFoundError,
)

BASE_URL = "https://bible-api.com"

PASSAGE_FIXTURE = {
    "reference": "John 3:16",
    "verses": [
        {
            "book_id": "JHN",
            "book_name": "John",
            "chapter": 3,
            "verse": 16,
            "text": "For God so loved the world...\n",
        }
    ],
    "text": "For God so loved the world...\n",
    "translation_id": "web",
    "translation_name": "World English Bible",
    "translation_note": "Public Domain",
}

CHAPTER_FIXTURE = {
    "translation": {
        "identifier": "web",
        "name": "World English Bible",
        "language": "English",
        "language_code": "eng",
        "license": "Public Domain",
    },
    "verses": [
        {"book_id": "JHN", "book": "John", "chapter": 3, "verse": 1, "text": "..."},
        {"book_id": "JHN", "book": "John", "chapter": 3, "verse": 36, "text": "..."},
    ],
}

RANDOM_FIXTURE = {
    "translation": {
        "identifier": "web",
        "name": "World English Bible",
        "language": "English",
        "language_code": "eng",
        "license": "Public Domain",
    },
    "random_verse": {
        "book_id": "1KI",
        "book": "1 Kings",
        "chapter": 3,
        "verse": 24,
        "text": "The king said, \u201cGet me a sword.\u201d\n",
    },
}


@pytest_asyncio.fixture
async def provider():
    p = BibleProvider(base_url=BASE_URL)
    yield p
    await p.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_get_passage_parses_reference_lookup(provider):
    respx.get(f"{BASE_URL}/john 3:16").mock(
        return_value=httpx.Response(200, json=PASSAGE_FIXTURE)
    )

    passage = await provider.get_passage("john 3:16")

    assert passage.reference == "John 3:16"
    assert passage.translation_id == "web"
    assert passage.verses[0].book_name == "John"
    assert passage.verses[0].verse == 16


@pytest.mark.asyncio
@respx.mock
async def test_get_passage_respects_translation_param(provider):
    route = respx.get(f"{BASE_URL}/john 3:16", params={"translation": "kjv"}).mock(
        return_value=httpx.Response(200, json={**PASSAGE_FIXTURE, "translation_id": "kjv"})
    )

    passage = await provider.get_passage("john 3:16", translation="kjv")

    assert route.called
    assert passage.translation_id == "kjv"


@pytest.mark.asyncio
@respx.mock
async def test_get_passage_404_raises_not_found(provider):
    respx.get(f"{BASE_URL}/not a real verse").mock(return_value=httpx.Response(404))

    with pytest.raises(BibleReferenceNotFoundError):
        await provider.get_passage("not a real verse")


@pytest.mark.asyncio
@respx.mock
async def test_get_chapter_parses_data_lookup(provider):
    respx.get(f"{BASE_URL}/data/web/JHN/3").mock(
        return_value=httpx.Response(200, json=CHAPTER_FIXTURE)
    )

    chapter = await provider.get_chapter("jhn", 3)

    assert chapter.translation.identifier == "web"
    assert len(chapter.verses) == 2
    assert chapter.verses[0].book == "John"  # note: `book`, not `book_name`, on this endpoint


@pytest.mark.asyncio
@respx.mock
async def test_get_random_verse_scoped_to_books(provider):
    respx.get(f"{BASE_URL}/data/web/random/MAT,MRK,LUK,JHN").mock(
        return_value=httpx.Response(200, json=RANDOM_FIXTURE)
    )

    result = await provider.get_random_verse(book_ids="MAT,MRK,LUK,JHN")

    assert result.random_verse.book_id == "1KI"


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_retries_then_raises(provider):
    route = respx.get(f"{BASE_URL}/john 3:16").mock(return_value=httpx.Response(429))

    with pytest.raises(BibleRateLimitedError):
        await provider.get_passage("john 3:16")

    # stop_after_attempt(4) -> exactly 4 calls before giving up
    assert route.call_count == 4


@pytest.mark.asyncio
@respx.mock
async def test_connection_error_wrapped(provider):
    respx.get(f"{BASE_URL}/john 3:16").mock(side_effect=httpx.ConnectError("boom"))

    with pytest.raises(BibleAPIUnavailableError):
        await provider.get_passage("john 3:16")