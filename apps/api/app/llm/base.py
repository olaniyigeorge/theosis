from abc import ABC, abstractmethod
from typing import Any

class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def generate_structured(
        self, system_prompt: str, user_prompt: str, json_schema: dict
    ) -> dict[str, Any]:
        """Return a dict validated against json_schema."""
        ...