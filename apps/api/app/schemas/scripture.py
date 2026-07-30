from __future__ import annotations

from pydantic import BaseModel

# NOTE: I don't have the current content of this file — if scripture.py
# already defines models (used by routers/scripture.py), merge these in
# rather than overwrite the file wholesale. Names below are deliberately
# specific (Bible* prefix) to reduce collision risk.
#
# Shapes below were confirmed against live bible-api.com responses on
# 2026-07-29, not guessed from docs alone:
#   GET /john%203:16                -> BiblePassage
#   GET /data/web/JHN/3              -> BibleChapter
#   GET /data/web/random             -> BibleRandomVerse
#
# bible-api.com is NOT consistent about the book-name field between its
# two endpoint families: the reference endpoint uses `book_name`, the
# /data endpoint uses `book`. BibleVerse below carries both as optional
# so one model covers both shapes instead of silently dropping one.


class BibleTranslation(BaseModel):
    identifier: str
    name: str
    language: str | None = None
    language_code: str | None = None
    license: str | None = None


class BibleVerse(BaseModel):
    book_id: str
    book: str | None = None       # present on /data/* responses
    book_name: str | None = None  # present on reference-lookup responses
    chapter: int
    verse: int
    text: str


class BiblePassage(BaseModel):
    """GET /{reference}?translation=xx — single verse or a verse range."""

    reference: str
    verses: list[BibleVerse]
    text: str
    translation_id: str
    translation_name: str
    translation_note: str | None = None


class BibleChapter(BaseModel):
    """GET /data/{translation}/{book_id}/{chapter} — every verse in a chapter."""

    translation: BibleTranslation
    verses: list[BibleVerse]


class BibleRandomVerse(BaseModel):
    """GET /data/{translation}/random[/{book_ids}]"""

    translation: BibleTranslation
    random_verse: BibleVerse