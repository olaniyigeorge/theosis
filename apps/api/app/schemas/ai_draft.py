from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.db.models.enums import NodeType
from app.schemas.node import NodeRead


class AIDraftRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=300)
    type: NodeType


class AIDraftResponse(BaseModel):
    node: NodeRead
    review_id: uuid.UUID