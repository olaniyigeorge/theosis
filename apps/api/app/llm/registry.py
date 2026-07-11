from functools import lru_cache
from config import settings
# from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiLLMProvider
# from .openai_provider import OpenAILLMProvider

@lru_cache
def get_llm_provider():
    match settings.LLM_PROVIDER:
        # case "anthropic": return AnthropicProvider(settings.ANTHROPIC_API_KEY)
        case "gemini":    return GeminiLLMProvider(settings.GEMINI_API_KEY)
        # case "openai":    return OpenAILLMProvider(settings.OPENAI_API_KEY)
        case _: raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")