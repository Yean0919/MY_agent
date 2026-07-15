"""Agent 单元测试"""

import pytest

from src.agents.orchestrator import Orchestrator


class TestOrchestrator:
    """编排器测试"""

    @pytest.mark.asyncio
    async def test_execute(self):
        """测试执行"""
        orchestrator = Orchestrator()
        result = await orchestrator.execute({"task": "test"})
        assert "results" in result
