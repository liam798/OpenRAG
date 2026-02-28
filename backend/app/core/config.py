"""应用配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "OpenRAG"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/openrag"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
