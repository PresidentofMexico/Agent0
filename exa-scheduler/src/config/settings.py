from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core
    openai_api_key: Optional[str] = None
    exa_api_secret: str = "dev-secret-key" # Default for dev, override in prod!
    log_level: str = "INFO"
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    
    # Defaults
    calendar_file: Path = data_dir / "calendar.json"
    reminders_file: Path = data_dir / "reminders.json"
    email_log_file: Path = data_dir / "email_outbox.log"
    memory_path: Path = data_dir / "memory"

    def ensure_dirs(self):
        """Creates necessary data directories."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memory_path.mkdir(parents=True, exist_ok=True)

# Singleton instance
settings = Settings()
settings.ensure_dirs()
