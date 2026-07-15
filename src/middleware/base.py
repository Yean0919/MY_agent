"""钩子基类"""

from abc import ABC, abstractmethod
from typing import Any


class BaseHook(ABC):
    """中间件钩子基类"""

    def __init__(self, name: str, priority: int = 100):
        if not name:
            raise ValueError("Hook name cannot be empty")
        self.name = name
        self.priority = priority

    @abstractmethod
    async def on_before(self, context: dict[str, Any]) -> dict[str, Any]:
        """执行前钩子

        Args:
            context: 上下文

        Returns:
            更新后的上下文
        """
        return context

    @abstractmethod
    async def on_after(self, context: dict[str, Any], result: Any) -> Any:
        """执行后钩子

        Args:
            context: 上下文
            result: 结果

        Returns:
            更新后的结果
        """
        return result

    @abstractmethod
    async def on_error(self, context: dict[str, Any], error: Exception) -> None:
        """错误钩子

        Args:
            context: 上下文
            error: 异常
        """
        pass
