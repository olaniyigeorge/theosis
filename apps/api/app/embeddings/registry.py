from functools import lru_cache
from app.config import settings
from .openai_provider import OpenAIEmbeddingProvider
from .gemini_provider import GeminiEmbeddingProvider

@lru_cache
def get_embedding_provider():
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider(settings.OPENAI_API_KEY)
    if settings.EMBEDDING_PROVIDER == "gemini":
        return GeminiEmbeddingProvider(settings.GEMINI_API_KEY)
    raise ValueError(f"Unknown embedding provider: {settings.EMBEDDING_PROVIDER}")