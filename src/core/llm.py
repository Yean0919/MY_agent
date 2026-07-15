"""LLM 调用层 - 统一对接 SenseNova / OpenAI 兼容 API"""

from __future__ import annotations

import logging
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

# 模块级 LLM 实例（懒初始化）
_llm_instance: ChatOpenAI | None = None


def _get_llm() -> ChatOpenAI:
    """获取或创建 LLM 实例（单例）"""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    settings = get_settings()
    provider = settings.llm.default_provider
    model = settings.llm.default_model
    base_url = settings.llm.base_url

    if provider == "openai":
        api_key = settings.openai.api_key.get_secret_value() if settings.openai.api_key else ""
        _llm_instance = ChatOpenAI(
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
        _llm_instance = ChatOpenAI(
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
    return _llm_instance


async def call_llm(
    messages: list[dict[str, Any]],
    *,
    system_prompt: str | None = None,
) -> str:
    """调用 LLM 并返回文本结果

    Args:
        messages: 对话消息列表，每项为 {"role": "user"|"assistant"|"system", "content": "..."}
        system_prompt: 可选的系统提示，会插入到消息列表开头

    Returns:
        LLM 返回的文本内容

    Raises:
        RuntimeError: LLM 调用失败
    """
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        llm = _get_llm()
        # 使用 streaming 模式避免 surrogate 字符序列化问题
        content_parts: list[str] = []
        async for chunk in llm.astream(messages):
            if hasattr(chunk, "content") and chunk.content:
                content_parts.append(str(chunk.content))
        content = "".join(content_parts)
        if not content:
            content = ""
        # 清理非法 Unicode surrogate 字符（SenseNova API 可能返回）
        content = content.encode("utf-8", errors="replace").decode("utf-8")
        content = "".join(ch for ch in content if not (0xDC00 <= ord(ch) <= 0xDFFF))
        return content
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        raise RuntimeError(f"LLM call failed: {e}") from e


def reset_llm() -> None:
    """重置 LLM 实例（用于测试或配置变更）"""
    global _llm_instance
    _llm_instance = None
