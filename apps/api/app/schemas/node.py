from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.enums import ConfidenceLevel, NodeType, ReviewStatus
from app.schemas.node_data import BeingData, StorySlotData


class CreateBeingNode(BaseModel):
    type: Literal[NodeType.BEING]
    data: BeingData


class CreateStorySlotNode(BaseModel):
    type: Literal[NodeType.STORY_SLOT]
    data: StorySlotData


NodeCreate = Annotated[
    CreateBeingNode | CreateStorySlotNode,
    Field(discriminator="type"),
]


class NodeRead(BaseModel):
    id: UUID
    type: NodeType
    data: Annotated[
        BeingData | StorySlotData,
        Field(discriminator="node_type"),
    ]
    confidence: ConfidenceLevel
    review_status: ReviewStatus

    model_config = ConfigDict(from_attributes=True)



class NodePage(BaseModel):
    items: list[NodeRead]
    total: int
    limit: int
    offset: int



class JourneyStep(BaseModel):
    story_slot: NodeRead
    relationship_type: str
    direction: Literal["outgoing", "incoming"]
    confidence: ConfidenceLevel
    notes: str | None = None


class BeingJourney(BaseModel):
    being: NodeRead
    steps: list[JourneyStep]