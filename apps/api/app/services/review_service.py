from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.review import ReviewCreate
from app.db.models.enums import ReviewDecision, ReviewStatus, ScriptureEntityType
from app.db.models.node import Node
from app.db.models.review import Review
from app.shared.exceptions import DuplicatePendingReviewError, EntityNotFoundError, ReviewNotFoundError, ReviewNotPendingError, UnsupportedReviewEntityError



class ReviewService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def approve(self, review_id: uuid.UUID) -> Review:
        # FOR UPDATE locks both rows so two concurrent approve calls on the
        # same review can't both pass the pending-status check below.
        review = (
            await self.session.execute(
                select(Review).where(Review.id == review_id).with_for_update()
            )
        ).scalar_one_or_none()

        if review is None:
            raise ReviewNotFoundError(f"Review {review_id} not found")

        if review.entity_type != ScriptureEntityType.NODE:
            raise UnsupportedReviewEntityError(
                f"Review {review_id} targets {review.entity_type.value}, not a node"
            )

        if review.status != ReviewStatus.IN_REVIEW:
            raise ReviewNotPendingError(
                f"Review {review_id} is not pending (status={review.status.value})"
            )

        node = (
            await self.session.execute(
                select(Node).where(Node.id == review.entity_id).with_for_update()
            )
        ).scalar_one_or_none()

        if node is None:
            raise ReviewNotFoundError(f"Node {review.entity_id} referenced by review not found")

        review.decision = ReviewDecision.APPROVED
        review.status = ReviewStatus.APPROVED  # see note below
        node.review_status = ReviewStatus.PUBLISHED

        try:
            await self.session.commit()
            await self.session.refresh(review)
            await self.session.refresh(node)
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        return review
    




    async def create(self, payload: ReviewCreate) -> Review:
        if payload.entity_type == ScriptureEntityType.NODE:
            node = (
                await self.session.execute(select(Node).where(Node.id == payload.entity_id))
            ).scalar_one_or_none()
            if node is None:
                raise EntityNotFoundError(f"Node {payload.entity_id} not found")
        else:
            # Edge review isn't wired up anywhere else in the service — same
            # gap flagged in approve(). Failing loudly here rather than
            # silently creating a review nothing can ever resolve.
            raise UnsupportedReviewEntityError(
                f"Review creation for entity_type={payload.entity_type.value} is not supported yet"
            )

        existing = (
            await self.session.execute(
                select(Review).where(
                    Review.entity_type == payload.entity_type,
                    Review.entity_id == payload.entity_id,
                    Review.status == ReviewStatus.IN_REVIEW,
                )
            )
        ).scalar_one_or_none()

        if existing is not None:
            raise DuplicatePendingReviewError(
                f"Entity {payload.entity_id} already has a pending review ({existing.id})"
            )

        review = Review(
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            status=ReviewStatus.IN_REVIEW,
            reviewer=payload.reviewer,
            notes=payload.notes,
        )
        self.session.add(review)

        try:
            await self.session.commit()
            await self.session.refresh(review)
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        return review