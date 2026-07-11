
class NodeNotFoundError(Exception):
    pass

class NodeNotBeingError(Exception):
    pass

class EntityNotFoundError(Exception):
    pass

class DuplicatePendingReviewError(Exception):
    pass

class ReviewNotFoundError(Exception):
    pass


class ReviewNotPendingError(Exception):
    pass


class UnsupportedReviewEntityError(Exception):
    """Review targets an Edge, not a Node — Edge approval isn't wired up
    yet, so this fails loudly instead of silently doing nothing to a node."""
