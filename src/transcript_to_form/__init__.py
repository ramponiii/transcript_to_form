from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    openai_api_key: str
    chroma_host: str
    chroma_port: int

    model_config = SettingsConfigDict(env_file=".env")


env_settings = EnvSettings()

__all__ = ["env_settings", "logger"]
