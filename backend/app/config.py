import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Ensure root .env is loaded
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReachOS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Nebius Token Factory / Nemotron models
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "")
    NEBIUS_BASE_URL: str = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/")
    
    NEMOTRON_FAST_MODEL: str = os.getenv("NEMOTRON_FAST_MODEL", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B")
    NEMOTRON_REASONING_MODEL: str = os.getenv("NEMOTRON_REASONING_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    NEMOTRON_DEEP_MODEL: str = os.getenv("NEMOTRON_DEEP_MODEL", "nvidia/Nemotron-3-Ultra-550b-a55b")

    # Tavily Web Research
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # Email Config
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "mock")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "outreach@reachos.ai")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./reachos.db")

    # Flags
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore")

settings = Settings()
