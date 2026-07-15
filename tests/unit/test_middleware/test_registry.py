"""钩子注册表单元测试"""

import pytest

from src.middleware.hooks import LoggingHook
from src.middleware.registry import HookRegistry


class TestHookRegistry:
    """钩子注册表测试"""

    def test_register_unregister(self):
        """测试注册和注销"""
        registry = HookRegistry()
        hook = LoggingHook()

        registry.register(hook)
        registry.unregister("logging")

    @pytest.mark.asyncio
    async def test_execute_before(self):
        """测试执行 before 钩子"""
        registry = HookRegistry()
        registry.register(LoggingHook())

        context = {}
        result = await registry.execute_before(context)

        assert "_start_time" in result

    @pytest.mark.asyncio
    async def test_execute_after(self):
        """测试执行 after 钩子"""
        registry = HookRegistry()
        registry.register(LoggingHook())

        context = {"_start_time": 0}
        result = await registry.execute_after(context, "test_result")

        assert result == "test_result"
