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


class BibleReferenceNotFoundError(Exception):
    """bible-api.com returned 404 for a reference, chapter, or random-verse
    lookup (bad book id, out-of-range chapter/verse, etc.)."""


class BibleAPIUnavailableError(Exception):
    """Network-level failure calling bible-api.com — timeout, DNS, connection
    refused. Distinct from a 404 (not found) or a 429 (rate limited)."""


class BibleRateLimitedError(Exception):
    """bible-api.com returned 429. bible-api.com's stated limit is 15
    requests / 30s per IP — BibleProvider retries this with backoff before
    it ever reaches a caller, so seeing this means retries were exhausted."""


class LLMGenerationError(Exception):
    """An LLM provider returned no usable content (empty choices, null
    content, or content that failed json.loads / schema validation)."""