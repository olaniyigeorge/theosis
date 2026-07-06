from openai import AsyncOpenAI
from .base import EmbeddingProvider, EmbeddingResult

class OpenAIEmbeddingProvider(EmbeddingProvider):
    provider_name = "openai"
    model_name = "text-embedding-3-small"
    dimension = 1536

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        resp = await self.client.embeddings.create(
            model=self.model_name, input=texts
        )
        return [
            EmbeddingResult(d.embedding, self.provider_name, self.model_name, self.dimension)
            for d in resp.data
        ]