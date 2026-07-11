from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BeingNature(StrEnum):
    DIVINE = "divine"
    ANGELIC = "angelic"
    HUMAN = "human"
    DEMONIC = "demonic"
    COLLECTIVE = "collective"
    OTHER = "other"


class StorySlotKind(StrEnum):
    NARRATIVE = "narrative"
    EVENT = "event"
    PERIOD = "period"
    DISCOURSE = "discourse"
    TEACHING = "teaching"
    MIRACLE = "miracle"
    JOURNEY = "journey"
    BATTLE = "battle"
    OTHER = "other"


class Granularity(StrEnum):
    ARC = "arc"
    EPISODE = "episode"
    SCENE = "scene"


class BeingData(BaseModel):
    node_type: Literal["being"] = "being"

    name: str = Field(..., min_length=1, max_length=150)
    aliases: list[str] = Field(default_factory=list)
    nature: BeingNature
    description: str = Field(..., min_length=1)
    roles: list[str] = Field(default_factory=list)
    is_collective: bool = False
    themes: list[str] = Field(default_factory=list)

    @field_validator("aliases", "roles", "themes")
    @classmethod
    def _strip_and_dedupe(cls, v: list[str]) -> list[str]:
        seen = []
        for item in v:
            item = item.strip()
            if item and item not in seen:
                seen.append(item)
        return seen
    
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)



class StorySlotData(BaseModel):
    node_type: Literal["story_slot"] = "story_slot"

    title: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1)
    kind: StorySlotKind
    granularity: Granularity
    narrative_order: int | None = None   # position in overall canonical timeline, nullable while unplaced
    location: str | None = None
    chronology_label: str | None = Field(
        default=None,
        max_length=200,
        description="Human-readable, potentially uncertain chronology.",
    )      # free text: "pre-flood", "exodus era" — too fuzzy for a real date range
    chronology_note: str | None = Field(default=None, max_length=2_000)
    themes: list[str] = Field(default_factory=list)

    @field_validator("themes")
    @classmethod
    def _strip_and_dedupe(cls, v: list[str]) -> list[str]:
        seen = []
        for item in v:
            item = item.strip()
            if item and item not in seen:
                seen.append(item)
        return seen
    
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

