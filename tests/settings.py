from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    promptlayer_api_key: str = Field(alias="PROMPTLAYER_API_KEY")
    promptlayer_report_id: int = Field(alias="PROMPTLAYER_REPORT_ID")
    promptlayer_base_url: str = Field(
        default="https://api.promptlayer.com",
        alias="PROMPTLAYER_BASE_URL",
    )
    default_score_threshold: float = 80.0
    poll_interval_seconds: int = 5
    timeout_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
