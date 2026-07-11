from __future__ import annotations

import json

from google import genai
from google.genai import types
from pydantic import BaseModel

from .base import LLMProvider


class GeminiLLMProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> dict:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_model,  # pass the class, not .model_json_schema()
            ),
        )

        if response.text is None:
            raise ValueError("Gemini returned no text content")

        # response.parsed also exists (pre-validated instance) but going through
        # json.loads keeps this symmetric with how ai_drafts.py already handles
        # provider output — one validation path regardless of which provider ran.
        return json.loads(response.text)