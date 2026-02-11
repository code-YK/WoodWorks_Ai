from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Application
    app_name: str = Field(default="WoodWorksAI")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    # Database (ABSOLUTE PATH)
    database_url: str = Field(
        default=f"sqlite:///{BASE_DIR / 'woodworks_ai.db'}"
    )
    db_echo: bool = False

    # Logging (APP-LEVEL, NOT app_log)
    log_level: str = "INFO"
    log_dir: str = Field(
        default=str(BASE_DIR / "logs")
    )
    log_max_bytes: int = 10_485_760  # 10 MB
    log_backup_count: int = 5

    # Groq LLM
    groq_api_key: str
    groq_model: str = "llama-3.1-70b-versatile"
    groq_temperature: float = 0.2
    groq_max_tokens: int = 2048

    # Streamlit
    streamlit_host: str = "localhost"
    streamlit_port: int = 8501

    # Agent Behavior
    enable_human_override: bool = True
    max_agent_retries: int = 2

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
