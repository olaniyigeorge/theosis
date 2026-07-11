from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db_session
from app.schemas.ai_draft import AIDraftRequest, AIDraftResponse
from app.services.ai_drafts import AIDraftGenerationError, AIDraftService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/draft", response_model=AIDraftResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_draft(
    payload: AIDraftRequest,
    session: AsyncSession = Depends(get_async_db_session),
) -> AIDraftResponse:
    service = AIDraftService(session)

    try:
        return await service.generate_and_create(payload)
    except AIDraftGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error