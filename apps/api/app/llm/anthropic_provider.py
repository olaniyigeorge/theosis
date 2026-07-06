import anthropic, json
from .base import LLMProvider

class AnthropicProvider(LLMProvider):
    provider_name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate_structured(self, system_prompt, user_prompt, json_schema):
        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{"name": "emit", "description": "Emit the structured draft", "input_schema": json_schema}],
            tool_choice={"type": "tool", "name": "emit"},
        )
        tool_block = next(b for b in resp.content if b.type == "tool_use")
        return tool_block.input