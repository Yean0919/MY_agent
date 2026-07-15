"""内置钩子实现"""

import time
from typing import Any

from src.middleware.base import BaseHook


class LoggingHook(BaseHook):
    """日志钩子"""

    def __init__(self) -> None:
        super().__init__(name="logging", priority=10)

    async def on_before(self, context: dict[str, Any]) -> dict[str, Any]:
        context["_start_time"] = time.time()
        # TODO: 记录日志
        return context

    async def on_after(self, context: dict[str, Any], result: Any) -> Any:
        _duration = time.time() - context.get("_start_time", 0)
        # TODO: 记录日志 (_duration)
        return result

    async def on_error(self, context: dict[str, Any], error: Exception) -> None:
        # TODO: 记录错误日志
        pass


class MetricsHook(BaseHook):
    """指标钩子"""

    def __init__(self) -> None:
        super().__init__(name="metrics", priority=20)
        self._metrics: dict[str, Any] = {}

    async def on_before(self, context: dict[str, Any]) -> dict[str, Any]:
        context["_start_time"] = time.time()
        return context

    async def on_after(self, context: dict[str, Any], result: Any) -> Any:
        duration = time.time() - context.get("_start_time", 0)
        # 记录指标
        operation = context.get("operation", "unknown")
        self._metrics[operation] = {
            "duration": duration,
            "success": True,
        }
        return result

    async def on_error(self, context: dict[str, Any], error: Exception) -> None:
        operation = context.get("operation", "unknown")
        self._metrics[operation] = {
            "duration": time.time() - context.get("_start_time", 0),
            "success": False,
            "error": str(error),
        }

    def get_metrics(self) -> dict[str, Any]:
        """获取指标

        Returns:
            指标字典
        """
        return self._metrics.copy()
