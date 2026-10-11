import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    COLAB_API_URL: str = Field(default="https://your-colab-tunnel-url.ngrok-free.app")
    COLAB_TIMEOUT_SECONDS: int = 180
    FALLBACK_TO_MOCK_IF_OFFLINE: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

