"""pydantic-settings 配置类"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# 将 .env 加载到 os.environ，供 _parse_model_profiles 等函数读取
load_dotenv()


class ModelProfile(BaseModel):
    """单个模型 profile 配置（从环境变量 LLM_PROFILE_<NAME>_<KEY> 加载）"""

    provider: Literal["anthropic", "openai", "google", "faux"] = "openai"
    model: str = ""
    base_url: str = ""
    api_key: SecretStr | None = None
    temperature: float = 0.3


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

    # 多模型配置（运行时填充，不由 pydantic-settings 自动解析）
    model_profiles: dict[str, ModelProfile] = Field(default_factory=dict)
    agent_models: dict[str, str] = Field(default_factory=dict)


def _parse_model_profiles() -> dict[str, ModelProfile]:
    """从环境变量解析模型 profile

    格式: LLM_PROFILE_<NAME>_<KEY>=value
    例如: LLM_PROFILE_CODER_MODEL=sensenova-6.7-flash-lite
    """
    profiles: dict[str, dict[str, str]] = {}
    prefix = "LLM_PROFILE_"

    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        rest = key[len(prefix):]
        parts = rest.split("_", 1)
        if len(parts) != 2 or not value:
            continue
        profile_name, field_name = parts[0].lower(), parts[1].lower()
        if profile_name not in profiles:
            profiles[profile_name] = {}
        profiles[profile_name][field_name] = value

    result: dict[str, ModelProfile] = {}
    for name, fields in profiles.items():
        try:
            # api_key 需要特殊处理
            api_key_val = fields.pop("api_key", None)
            profile = ModelProfile(**fields)
            if api_key_val:
                profile.api_key = SecretStr(api_key_val)
            result[name] = profile
        except Exception:
            pass  # 忽略配置错误的 profile
    return result


def _parse_agent_models() -> dict[str, str]:
    """从环境变量解析 Agent 模型映射

    格式: LLM_AGENT_MODEL_<AGENT_NAME>=profile_name
    例如: LLM_AGENT_MODEL_CODER=deepseek
    """
    mapping: dict[str, str] = {}
    prefix = "LLM_AGENT_MODEL_"

    for key, value in os.environ.items():
        if not key.startswith(prefix) or not value:
            continue
        agent_name = key[len(prefix):].lower()
        mapping[agent_name] = value.lower()

    return mapping


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    settings.model_profiles = _parse_model_profiles()
    settings.agent_models = _parse_agent_models()
    return settings
