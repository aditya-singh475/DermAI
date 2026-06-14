"""Application configuration using Pydantic Settings."""

import os
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables / .env file."""

    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    MODEL_PATH: str
    CLASS_MAP_PATH: str
    CORS_ORIGINS: list[str] = ["*"]
    ENVIRONMENT: str = "development"
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_DIR: str

    def __init__(self):
        # Load .env file from project root if it exists
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        load_dotenv(env_path)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.db"),
        )
        self.MODEL_PATH = os.getenv(
            "MODEL_PATH",
            os.path.join(base_dir, "model", "models", "skin_model.h5"),
        )
        self.CLASS_MAP_PATH = os.getenv(
            "CLASS_MAP_PATH",
            os.path.join(base_dir, "model", "models", "class_indices.json"),
        )
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        cors = os.getenv("CORS_ORIGINS", "*")
        self.CORS_ORIGINS = [s.strip() for s in cors.split(",")]
        self.UPLOAD_DIR = os.getenv(
            "UPLOAD_DIR",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"),
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
