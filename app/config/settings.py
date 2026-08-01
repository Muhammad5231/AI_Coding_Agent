"""
Application Configuration and Settings Definitions.
Provides centralized path management and default configuration key-value pairs.
"""

from pathlib import Path
from typing import Any, Dict


class Config:
    """Central configuration class maintaining directory paths and defaults."""

    # Base directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    APP_DIR: Path = BASE_DIR / "app"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    
    # Sub-storage paths
    DB_DIR: Path = STORAGE_DIR / "database"
    PROJECTS_DIR: Path = STORAGE_DIR / "projects"
    LOGS_DIR: Path = STORAGE_DIR / "logs"

    DB_FILE: Path = DB_DIR / "studio.db"
    LOG_FILE: Path = LOGS_DIR / "app.log"

    # LLM Settings Defaults
    DEFAULT_SETTINGS: Dict[str, Any] = {
        "api_type": "ollama",  # 'ollama' or 'openai'
        "api_url": "http://localhost:11434",
        "model_name": "llama3:8b",
        "temperature": 0.2,
        "max_tokens": 4096,
        "timeout": 120,
        "system_prompt": (
            "You are an expert software architect and developer. When asked to generate a project, "
            "provide a complete, modular, clean implementation. Structure files explicitly using header tags:\n"
            "### File: relative/path/to/filename.ext\n```language\ncode here\n```"
        )
    }

    @classmethod
    def initialize_directories(cls) -> None:
        """Ensure all required local storage directories exist."""
        cls.DB_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)