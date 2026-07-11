from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.enums import NodeType, ReviewStatus, ScriptureEntityType
from app.db.models.node import Node
from app.db.models.review import Review
from app.llm.registry import get_llm_provider  # ASSUMPTION — see note below
from app.schemas.ai_draft import AIDraftRequest, AIDraftResponse
from app.schemas.node import NodeRead
from app.schemas.node_data import BeingData, StorySlotData

AI_REVIEWER = "ai-system"

_DATA_MODEL_BY_TYPE = {
    NodeType.BEING: BeingData,
    NodeType.STORY_SLOT: StorySlotData,
}


class AIDraftGenerationError(Exception):
    """LLM call failed, returned invalid JSON, or output failed schema validation."""


class AIDraftService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate_and_create(self, payload: AIDraftRequest) -> AIDraftResponse:
        data_model = _DATA_MODEL_BY_TYPE[payload.type]

        raw = await self._generate_structured(payload.topic, payload.type, data_model)

        try:
            validated_data = data_model.model_validate(raw)
        except ValidationError as error:
            raise AIDraftGenerationError(
                f"LLM output failed {data_model.__name__} validation: {error}"
            ) from error

        # NOTE: deliberately not reusing NodeService.create() here — that method
        # commits internally, and this flow needs the Node + Review to land in
        # the same transaction so they either both succeed or both roll back.
        node = Node(
            type=payload.type,
            data=validated_data.model_dump(mode="json", exclude={"node_type"}),
            confidence="unknown",
            review_status=ReviewStatus.DRAFT,
        )
        self.session.add(node)

        try:
            # flush (not commit) — need node.id for the Review FK-equivalent
            # (entity_id) while staying inside one transaction.
            await self.session.flush()
        except IntegrityError as error:
            await self.session.rollback()
            raise AIDraftGenerationError("Could not persist generated node") from error

        review = Review(
            entity_type=ScriptureEntityType.NODE,
            entity_id=node.id,
            status=ReviewStatus.IN_REVIEW,
            reviewer=AI_REVIEWER,
        )
        self.session.add(review)

        try:
            await self.session.commit()
            await self.session.refresh(node)
            await self.session.refresh(review)
        except SQLAlchemyError as error:
            await self.session.rollback()
            raise AIDraftGenerationError("Could not persist review record") from error

        return AIDraftResponse(node=NodeRead.model_validate(node), review_id=review.id)


    async def _generate_structured(
        self, topic: str, node_type: NodeType, data_model: type[BaseModel]
    ) -> dict:
        provider = get_llm_provider()

        system_prompt = (
            "You are a biblical knowledge graph assistant. Generate factually "
            "grounded structured data. Respond only with the requested schema."
        )
        user_prompt = f"Generate a JSON object describing the biblical {node_type.value} '{topic}'."

        return await provider.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=data_model,
        )