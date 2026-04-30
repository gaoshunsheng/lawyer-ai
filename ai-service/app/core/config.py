from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "律师AI助手 - AI服务"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # 服务端口
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lawyer_ai"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # Elasticsearch配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # LLM配置
    LLM_PROVIDER: str = "openai"  # openai, zhipu, custom
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ZHIPU_API_KEY: Optional[str] = None
    ZHIPU_MODEL: str = "glm-4"

    # Embedding配置
    EMBEDDING_PROVIDER: str = "local"  # openai, local
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh"
    EMBEDDING_DIMENSION: int = 1024

    # RAG配置
    RAG_TOP_K: int = 10
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_MAX_CONTEXT_LENGTH: int = 8000

    # 文档处理配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # JWT配置
    JWT_SECRET_KEY: str = "lawyer-ai-assistant-jwt-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 7200

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


settings = get_settings()
