"""tenacity 重试装饰器"""

from collections.abc import Callable
from typing import Any, TypeVar

from tenacity import retry, stop_after_attempt, wait_exponential

__all__ = ["retry", "retry_decorator"]

T = TypeVar("T", bound=Callable[..., Any])


def retry_decorator(max_attempts: int = 3, wait_seconds: int = 1) -> Callable[[T], T]:
    """重试装饰器

    Args:
        max_attempts: 最大尝试次数
        wait_seconds: 等待秒数

    Returns:
        装饰器
    """
    if max_attempts <= 0:
        raise ValueError("max_attempts must be positive")
    if wait_seconds <= 0:
        raise ValueError("wait_seconds must be positive")

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=wait_seconds, max=wait_seconds * max_attempts),
        reraise=True,
    )
