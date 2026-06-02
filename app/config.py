from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "document-intelligence-api"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS
    cors_origins: str = "*"

    # File Upload
    max_file_size_mb: int = 20
    upload_dir: str = "/tmp/uploads"
    keep_uploaded_files: bool = False

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_cache_dir: str = "/app/model_cache"

    # Vector Store
    vector_store: str = "chroma"  # qdrant | chroma
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "document_chunks"
    chroma_persist_dir: str = "./data/chroma"

    # Retrieval
    retrieval_top_k: int = 5
    retrieval_min_score: float = 0.3

    # LLM
    llm_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.1

    # Rate Limiting
    rate_limit_per_minute: int = 10

    # Evaluation
    eval_output_dir: str = "./eval_results"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
