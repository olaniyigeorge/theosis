from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models.enums import ReviewDecision, ReviewStatus, ScriptureEntityType

class ReviewCreate(BaseModel):
    entity_type: ScriptureEntityType
    entity_id: uuid.UUID
    reviewer: str = Field(..., min_length=1, max_length=100)
    notes: str | None = None

    
class ReviewRead(BaseModel):
    id: uuid.UUID
    entity_type: ScriptureEntityType
    entity_id: uuid.UUID
    status: ReviewStatus
    decision: ReviewDecision | None
    reviewer: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True