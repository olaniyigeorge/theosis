from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DOMAIN: str = "http://localhost:8000"
    DATABASE_URL: str
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_DIMENSION: int = 1536
    LLM_PROVIDER: str = "anthropic"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    BIBLE_API_BASE_URL: str = "https://bible-api.com"
    ADMIN_TOKEN: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()