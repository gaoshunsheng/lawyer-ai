from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "律智通"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/lawyer_ai"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_STORAGE_BUCKET: str = "law-files"

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # 智谱AI
    ZHIPU_API_KEY: str = ""
    ZHIPU_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
