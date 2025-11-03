from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Config(BaseSettings):
    max_activity_nesting_level: int = Field(
        default=3,
        alias="MAX_ACTIVITY_NESTING_LEVEL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
