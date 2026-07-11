from uuid import UUID

from sqlalchemy import Integer, case, cast, select, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.models.enums import ConfidenceLevel, NodeType, ReviewStatus
from app.db.models.node import Node
from app.schemas.node import NodeCreate
from app.db.models.edge import Edge
from app.shared.exceptions import NodeNotBeingError, NodeNotFoundError


class NodeConflictError(Exception):
    pass


class NodeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: NodeCreate) -> Node:
        node = Node(
            type=payload.type,
            data=payload.data.model_dump(mode="json"),
            confidence="unknown",
            review_status=ReviewStatus.DRAFT,
        )
        self.session.add(node)

        try:
            await self.session.commit()
            await self.session.refresh(node)
        except IntegrityError as error:
            await self.session.rollback()
            raise NodeConflictError from error
        except SQLAlchemyError:
            await self.session.rollback()
            raise

        return node

    async def get_by_id(self, node_id: UUID) -> Node | None:
        return await self.session.get(Node, node_id)

    async def list_nodes(
        self,
        *,
        node_type: NodeType | None = None,
        review_status: ReviewStatus | None = None,
        confidence: ConfidenceLevel | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Node], int]:
        filters = []

        if node_type is not None:
            filters.append(Node.type == node_type)

        if review_status is not None:
            filters.append(Node.review_status == review_status)

        if confidence is not None:
            filters.append(Node.confidence == confidence)

        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Node.data["name"].astext.ilike(pattern),
                    Node.data["title"].astext.ilike(pattern),
                    Node.data["description"].astext.ilike(pattern),
                    Node.data["summary"].astext.ilike(pattern),
                )
            )

        total_statement = select(func.count()).select_from(Node).where(*filters)
        total = await self.session.scalar(total_statement) or 0

        statement = (
            select(Node)
            .where(*filters)
            .order_by(Node.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.scalars(statement)

        return list(result), total
    
    async def get_journey(
        self,
        being_id: UUID,
    ) -> tuple[Node, list[tuple[Node, Edge, str]]]:
        being = await self.session.get(Node, being_id)

        if being is None:
            raise NodeNotFoundError

        if being.type != NodeType.BEING:
            raise NodeNotBeingError

        story_slot = aliased(Node)

        connected_node_id = case(
            (Edge.source_id == being_id, Edge.target_id),
            else_=Edge.source_id,
        )

        direction = case(
            (Edge.source_id == being_id, "outgoing"),
            else_="incoming",
        ).label("direction")

        narrative_order = cast(
            story_slot.data["narrative_order"].astext,
            Integer,
        )

        statement = (
            select(story_slot, Edge, direction)
            .join(story_slot, story_slot.id == connected_node_id)
            .where(
                or_(
                    Edge.source_id == being_id,
                    Edge.target_id == being_id,
                ),
                story_slot.type == NodeType.STORY_SLOT,
            )
            .order_by(narrative_order.asc().nullslast(), Edge.created_at.asc())
        )

        rows = (await self.session.execute(statement)).all()

        return being, [
            (row[0], row[1], row[2])
            for row in rows
        ]