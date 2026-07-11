from .nodes import router as node_routes
from .ai import router as ai_routes
from .review import router as review_routes


router_list = [
    node_routes,
    ai_routes,
    review_routes
]




