from __future__ import annotations

import json

from openrouter import OpenRouter
from pydantic import BaseModel

from app.shared.exceptions import LLMGenerationError
from .base import LLMProvider

# NOTE on base.py vs GeminiLLMProvider: LLMProvider.generate_structured is
# declared with `json_schema: dict`, but the only working implementation
# (GeminiLLMProvider) actually takes `response_model: type[BaseModel]` and
# passes the class itself to the SDK. The abstract signature is stale —
# I've followed the real (Gemini) convention here rather than the ABC's,
# since that's what registry.py/ai_drafts.py actually call. Worth fixing
# base.py's annotation separately so the two don't keep drifting.


def _extract_text(content: str | list | None) -> str | None:
    """OpenRouter's ChatAssistantMessage.content is `str | list[ChatContentItems]
    | None` depending on model/response mode — normalize to a single string."""
    if content is None:
        return None
    if isinstance(content, str):
        return content
    parts = [getattr(item, "text", None) for item in content]
    parts = [p for p in parts if p]
    return "".join(parts) if parts else None


def _to_strict_json_schema(schema: dict) -> dict:
    """Recursively add "additionalProperties": false to every object node.

    Pydantic's model_json_schema() doesn't set this by default. OpenAI's
    strict structured-outputs mode requires it on every object — top level
    AND every nested object, including entries under "$defs" (pydantic puts
    nested models there, referenced via "$ref") — otherwise the provider
    400s with a generic "Provider returned error" and no clearer detail.
    Providers that don't enforce strict mode just ignore the extra key, so
    this is safe to apply unconditionally rather than only for OpenAI.
    """
    if schema.get("type") == "object":
        schema.setdefault("additionalProperties", False)
        for prop_schema in schema.get("properties", {}).values():
            _to_strict_json_schema(prop_schema)
    if "items" in schema:
        _to_strict_json_schema(schema["items"])
    for def_schema in schema.get("$defs", {}).values():
        _to_strict_json_schema(def_schema)
    return schema


class OpenRouterLLMProvider(LLMProvider):
    provider_name = "openrouter"

    def __init__(self, api_key: str, model: str = "openai/gpt-4o-mini"):
        self.client = OpenRouter(api_key=api_key)
        self.model = model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> dict:
        result = await self.client.chat.send_async(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"{system_prompt}\n\nRespond with a JSON object only.",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": _to_strict_json_schema(response_model.model_json_schema()),
                    "strict": True,
                },
            },
        )

        if not result.choices:
            raise LLMGenerationError("OpenRouter returned no choices")

        content = _extract_text(result.choices[0].message.content)
        if content is None:
            raise LLMGenerationError("OpenRouter returned no text content")

        # json.loads here (not response_model.model_validate_json) to stay
        # symmetric with GeminiLLMProvider — one validation path in
        # ai_drafts.py regardless of which provider ran.
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMGenerationError(f"OpenRouter returned non-JSON content: {exc}") from exc

    async def aclose(self) -> None:
        await self.client.__aexit__(None, None, None)


if __name__ == "__main__":
    # Manual smoke test — hits the real OpenRouter API. Run with:
    #   python -m app.llm.openrouter_provider
    # from apps/api (not `python app/llm/openrouter_provider.py` — that
    # doesn't put `app/` on sys.path and `from app.shared...` will fail).
    #
    # Guarded behind __name__ == "__main__" deliberately: this file is
    # imported by registry.py -> imported by the app on every boot, so any
    # module-level code here (not inside this block) runs on every startup.
    import asyncio

    from config import settings

    class DemoAnswer(BaseModel):
        answer: str

    async def _main() -> None:
        provider = OpenRouterLLMProvider(
            api_key=settings.OPENROUTER_API_KEY,
            model="openai/gpt-4o-mini",  # verify any model slug against
            # https://openrouter.ai/models — a made-up slug just 404s
        )
        try:
            result = await provider.generate_structured(
                system_prompt="You are Theosis agent. Answer concisely.",
                user_prompt="What are you?",
                response_model=DemoAnswer,
            )
            print(result)
        except Exception as exc:
            # BadRequestResponseError's top-level message is often just
            # "Provider returned error" — the actual reason (schema
            # rejected, bad key, no credits, etc.) is nested one level
            # deeper in .data.error.
            data = getattr(exc, "data", None)
            if data is not None:
                print("\ncode:", data.error.code)
                print("\nmessage:", data.error.message)
                print("\nmetadata:", data.error.metadata)
            else:
                print(repr(exc))
            raise
        finally:
            await provider.aclose()

    asyncio.run(_main())