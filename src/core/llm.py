"""LLM 调用层 - 统一对接 SenseNova / OpenAI 兼容 API，支持多模型 profile"""

from __future__ import annotations

import logging
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.config.settings import ModelProfile, get_settings

logger = logging.getLogger(__name__)

# 模块级 LLM 实例缓存：profile_name -> ChatOpenAI
_llm_cache: dict[str, ChatOpenAI] = {}

# 默认实例的缓存 key
_DEFAULT_KEY = "__default__"


def _create_llm_from_profile(profile: ModelProfile, profile_name: str = "default") -> ChatOpenAI:
    """从 ModelProfile 创建 LLM 实例"""
    api_key = profile.api_key.get_secret_value() if profile.api_key else ""
    if not api_key:
        # 降级：尝试从全局 settings 获取 api_key
        settings = get_settings()
        if profile.provider == "anthropic" and settings.anthropic.api_key:
            api_key = settings.anthropic.api_key.get_secret_value()
        elif settings.openai.api_key:
            api_key = settings.openai.api_key.get_secret_value()

    logger.info(
        "LLM created: profile=%s provider=%s model=%s base_url=%s",
        profile_name,
        profile.provider,
        profile.model,
        profile.base_url,
    )
    return ChatOpenAI(
        model=profile.model,
        api_key=SecretStr(api_key),
        base_url=profile.base_url,
        temperature=profile.temperature,
        timeout=30,
        max_retries=1,
    )


def _get_llm() -> ChatOpenAI:
    """获取默认 LLM 实例（向后兼容）"""
    if _DEFAULT_KEY in _llm_cache:
        return _llm_cache[_DEFAULT_KEY]

    settings = get_settings()
    provider = settings.llm.default_provider
    model = settings.llm.default_model
    base_url = settings.llm.base_url

    if provider == "openai":
        api_key = settings.openai.api_key.get_secret_value() if settings.openai.api_key else ""
        llm = ChatOpenAI(
            model=model,
            api_key=SecretStr(api_key),
            base_url=base_url,
            temperature=0.3,
            timeout=30,
            max_retries=1,
        )
    elif provider == "anthropic":
        api_key = (
            settings.anthropic.api_key.get_secret_value() if settings.anthropic.api_key else ""
        )
        llm = ChatOpenAI(
            model=model,
            api_key=SecretStr(api_key),
            base_url=base_url or "https://api.anthropic.com/v1",
            temperature=0.3,
            timeout=30,
            max_retries=1,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    logger.info("LLM initialized: provider=%s model=%s base_url=%s", provider, model, base_url)
    _llm_cache[_DEFAULT_KEY] = llm
    return llm


def get_llm_by_profile(profile_name: str) -> ChatOpenAI:
    """根据 profile 名称获取 LLM 实例（带缓存）

    Args:
        profile_name: 模型 profile 名称（对应 .env 中 LLM_PROFILE_<NAME> 配置）

    Returns:
        ChatOpenAI 实例

    Raises:
        ValueError: 找不到指定的 profile
    """
    if profile_name in _llm_cache:
        return _llm_cache[profile_name]

    settings = get_settings()
    profile = settings.model_profiles.get(profile_name)
    if not profile:
        raise ValueError(
            f"Model profile '{profile_name}' not found. "
            f"Available profiles: {list(settings.model_profiles.keys())}"
        )

    llm = _create_llm_from_profile(profile, profile_name)
    _llm_cache[profile_name] = llm
    return llm


def resolve_agent_profile(agent_name: str) -> str | None:
    """解析 Agent 对应的 model profile 名称

    Args:
        agent_name: Agent 名称

    Returns:
        profile 名称，或 None（使用默认模型）
    """
    settings = get_settings()
    return settings.agent_models.get(agent_name)


def _clean_content(content: str) -> str:
    """清理 LLM 返回内容中的非法字符"""
    content = content.encode("utf-8", errors="replace").decode("utf-8")
    return "".join(ch for ch in content if not (0xDC00 <= ord(ch) <= 0xDFFF))


async def call_llm(
    messages: list[dict[str, Any]],
    *,
    system_prompt: str | None = None,
    profile_name: str | None = None,
) -> str:
    """调用 LLM 并返回文本结果

    Args:
        messages: 对话消息列表
        system_prompt: 可选的系统提示
        profile_name: 可选的模型 profile 名称，为 None 时使用默认模型

    Returns:
        LLM 返回的文本内容

    Raises:
        RuntimeError: LLM 调用失败
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        llm = get_llm_by_profile(profile_name) if profile_name else _get_llm()

        # 使用 streaming 模式避免 surrogate 字符序列化问题
        content_parts: list[str] = []
        async for chunk in llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                content_parts.append(str(chunk.content))
        content = "".join(content_parts)
        if not content:
            content = ""
        content = _clean_content(content)
        return content
    except Exception as e:
        logger.error("LLM call failed (profile=%s): %s", profile_name, e)
        raise RuntimeError(f"LLM call failed: {e}") from e


def reset_llm() -> None:
    """重置所有 LLM 实例缓存"""
    global _llm_cache
    _llm_cache = {}
