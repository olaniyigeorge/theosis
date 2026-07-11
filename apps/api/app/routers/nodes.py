from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db_session
from app.schemas.node import BeingJourney, JourneyStep, NodeCreate, NodeRead, NodePage
from app.services.node_service import NodeConflictError, NodeService
from app.db.models.enums import ConfidenceLevel, NodeType, ReviewStatus
from app.shared.exceptions import NodeNotBeingError, NodeNotFoundError


router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.post("", response_model=NodeRead, status_code=status.HTTP_201_CREATED)
async def create_node(
    payload: NodeCreate,
    session: AsyncSession = Depends(get_async_db_session),
) -> NodeRead:
    service = NodeService(session)

    try:
        return await service.create(payload)
    except NodeConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create node",
        ) from error
    


@router.get("", response_model=NodePage)
async def list_nodes(
    node_type: NodeType | None = Query(default=None, alias="type"),
    review_status: ReviewStatus | None = None,
    confidence: ConfidenceLevel | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_async_db_session),
) -> NodePage:
    nodes, total = await NodeService(session).list_nodes(
        node_type=node_type,
        review_status=review_status,
        confidence=confidence,
        search=search,
        limit=limit,
        offset=offset,
    )
    return NodePage(items=nodes, total=total, limit=limit, offset=offset)

@router.get("/{node_id}", response_model=NodeRead)
async def get_node(
    node_id: UUID,
    session: AsyncSession = Depends(get_async_db_session),
) -> NodeRead:
    node = await NodeService(session).get_by_id(node_id)

    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    return node


@router.get("/{node_id}/journey", response_model=BeingJourney)
async def get_being_journey(
    node_id: UUID,
    session: AsyncSession = Depends(get_async_db_session),
) -> BeingJourney:
    try:
        being, steps = await NodeService(session).get_journey(node_id)
    except NodeNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        ) from error
    except NodeNotBeingError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Journey is only available for Being nodes",
        ) from error

    return BeingJourney(
        being=being,
        steps=[
            JourneyStep(
                story_slot=story_slot,
                relationship_type=edge.relationship_type,
                direction=direction,
                confidence=edge.confidence,
                notes=edge.notes,
            )
            for story_slot, edge, direction in steps
        ],
    )