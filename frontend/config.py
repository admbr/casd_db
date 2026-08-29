"""
Central configuration for the CASD Streamlit frontend.

Values are read from environment variables (optionally loaded from a
local .env file), so the same code can point at a local backend during
development or a deployed one in production without any code changes.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    APP_TITLE: str = "CASD"
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))


settings = Settings()
