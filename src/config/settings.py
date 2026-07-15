"""pydantic-settings 配置类"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM 提供者配置"""

    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    default_provider: Literal["anthropic", "openai", "google", "faux"] = "anthropic"
    default_model: str = "claude-sonnet-4-20250514"
    base_url: str = ""


class AnthropicSettings(BaseSettings):
    """Anthropic 配置"""

    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_", env_file=".env", extra="ignore")

    api_key: SecretStr | None = None
    timeout: int = 60


class OpenAISettings(BaseSettings):
    """OpenAI 配置"""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=".env", extra="ignore")

    api_key: SecretStr | None = None
    timeout: int = 60


class ChromaSettings(BaseSettings):
    """ChromaDB 配置"""

    model_config = SettingsConfigDict(env_prefix="CHROMA_", env_file=".env", extra="ignore")

    persist_dir: Path = Field(default=Path("./data/chroma"))


class Settings(BaseSettings):
    """全局配置聚合根"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 子命名空间
    llm: LLMSettings = Field(default_factory=LLMSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)

    # 基础配置
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["text", "json"] = "text"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    dashboard_port: int = 8501
    skill_dirs: list[str] = Field(default_factory=lambda: ["./skills"])
    mcp_config_path: Path = Field(default=Path("./config/mcp_servers.yaml"))


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
