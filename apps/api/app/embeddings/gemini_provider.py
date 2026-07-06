from google import genai
from google.genai import types
from .base import EmbeddingProvider, EmbeddingResult

class GeminiEmbeddingProvider(EmbeddingProvider):
    provider_name = "gemini"
    model_name = "gemini-embedding-001"
    dimension = 1536   # truncated via output_dimensionality — must match OpenAI's dim

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        results = []
        for text in texts:
            resp = await self.client.aio.models.embed_content(
                model=self.model_name,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=self.dimension,
                ),
            )
            results.append(EmbeddingResult(
                resp.embeddings[0].values, self.provider_name, self.model_name, self.dimension
            ))
        return results