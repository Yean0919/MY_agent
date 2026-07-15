"""中间件钩子单元测试"""

import pytest

from src.middleware.hooks import LoggingHook, MetricsHook


class TestLoggingHook:
    """日志钩子测试"""

    @pytest.mark.asyncio
    async def test_on_before(self):
        """测试 before 钩子"""
        hook = LoggingHook()
        context = {}

        result = await hook.on_before(context)

        assert "_start_time" in result

    @pytest.mark.asyncio
    async def test_on_after(self):
        """测试 after 钩子"""
        hook = LoggingHook()
        context = {"_start_time": 0}

        result = await hook.on_after(context, "test_result")

        assert result == "test_result"


class TestMetricsHook:
    """指标钩子测试"""

    @pytest.mark.asyncio
    async def test_on_before(self):
        """测试 before 钩子"""
        hook = MetricsHook()
        context = {}

        result = await hook.on_before(context)

        assert "_start_time" in result

    @pytest.mark.asyncio
    async def test_on_after(self):
        """测试 after 钩子"""
        hook = MetricsHook()
        context = {"_start_time": 0}

        result = await hook.on_after(context, "test_result")

        assert result == "test_result"
