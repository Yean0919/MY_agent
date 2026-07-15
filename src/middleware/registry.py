"""钩子注册表"""

from typing import Any

from src.middleware.base import BaseHook


class HookRegistry:
    """钩子注册表，管理所有钩子"""

    def __init__(self) -> None:
        self._hooks: list[BaseHook] = []

    def register(self, hook: BaseHook) -> None:
        """注册钩子

        Args:
            hook: 钩子实例
        """
        self._hooks.append(hook)
        self._hooks.sort(key=lambda h: h.priority)

    def unregister(self, name: str) -> None:
        """注销钩子

        Args:
            name: 钩子名称
        """
        self._hooks = [h for h in self._hooks if h.name != name]

    async def execute_before(self, context: dict[str, Any]) -> dict[str, Any]:
        """执行所有 before 钩子

        Args:
            context: 上下文

        Returns:
            更新后的上下文
        """
        for hook in self._hooks:
            context = await hook.on_before(context)
        return context

    async def execute_after(self, context: dict[str, Any], result: Any) -> Any:
        """执行所有 after 钩子

        Args:
            context: 上下文
            result: 结果

        Returns:
            更新后的结果
        """
        for hook in self._hooks:
            result = await hook.on_after(context, result)
        return result

    async def execute_error(self, context: dict[str, Any], error: Exception) -> None:
        """执行所有 error 钩子

        Args:
            context: 上下文
            error: 异常
        """
        for hook in self._hooks:
            await hook.on_error(context, error)

    def list_hooks(self) -> list[str]:
        """列出所有钩子名称

        Returns:
            钩子名称列表
        """
        return [h.name for h in self._hooks]

    def count(self) -> int:
        """获取钩子数量

        Returns:
            钩子数量
        """
        return len(self._hooks)
