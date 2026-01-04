from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "koo"
    APP_TIMEZONE: str = "Asia/Seoul"

    # Database
    DATABASE_URL: str

    # Milvus
    MILVUS_HOST: str = "127.0.0.1"
    MILVUS_PORT: int = 19530

    # Embedding
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "openai:text-embedding-3-small"
    EMBEDDING_DIM: int = 1536

    # LLM
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "openai-responses:gpt-4.1-mini"

    OPENAI_API_KEY: str | None = None

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_API_KEY: str | None = None

    # Notion
    NOTION_API_TOKEN: str | None = None

    # Etc
    TOPK: int = 8


settings = Settings()
