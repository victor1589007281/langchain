"""应用配置"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""

    # 基础配置
    APP_NAME: str = "LangChain API Service"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS 配置
    ALLOWED_ORIGINS: List[str] = ["*"]

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # LangChain 配置
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    # 向量存储配置
    VECTOR_STORE_PATH: str = "./data/vector_store"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # 速率限制
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 秒

    # 认证
    API_KEY_ENABLED: bool = False
    API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

