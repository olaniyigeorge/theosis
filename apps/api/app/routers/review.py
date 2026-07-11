from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.dependencies import get_async_db_session
from app.schemas.review import ReviewCreate, ReviewRead
from app.services.review_service import (
    ReviewNotFoundError,
    ReviewNotPendingError,
    ReviewService,
    UnsupportedReviewEntityError,
    
)
from app.shared.exceptions import DuplicatePendingReviewError, EntityNotFoundError

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{review_id}/approve", response_model=ReviewRead)
async def approve_review(
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_db_session),
) -> ReviewRead:
    review_service = ReviewService(session)

    try:
        return await review_service.approve(review_id)
    except ReviewNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ReviewNotPendingError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except UnsupportedReviewEntityError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    

@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    session: AsyncSession = Depends(get_async_db_session),
) -> ReviewRead:
    review_service = ReviewService(session)

    try:
        return await review_service.create(payload)
    except EntityNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except DuplicatePendingReviewError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except UnsupportedReviewEntityError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error