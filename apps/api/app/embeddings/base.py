
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class EmbeddingResult:
    vector: list[float]
    provider: str        # "openai" | "gemini"
    model: str            # e.g. "text-embedding-3-small"
    dimension: int

class EmbeddingProvider(ABC):
    provider_name: str
    model_name: str
    dimension: int

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        """Embed a batch of texts, returning one EmbeddingResult per input."""
        ...