"""多模型 Agent 支持测试"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.orchestrator import Orchestrator
from src.agents.roles.coder import CoderAgent
from src.agents.roles.reviewer import ReviewerAgent
from src.agents.roles.tester import TesterAgent
from src.core.agent import BaseAgent
from src.core.llm import call_llm, get_llm_by_profile, reset_llm, resolve_agent_profile


class TestModelProfile:
    """测试模型 profile 解析"""

    def test_resolve_agent_profile_from_env(self):
        """测试从环境变量解析 Agent 模型映射"""
        with patch.dict(os.environ, {"LLM_AGENT_MODEL_CODER": "deepseek"}):
            from src.config.settings import _parse_agent_models

            mapping = _parse_agent_models()
            assert mapping.get("coder") == "deepseek"

    def test_parse_model_profiles_from_env(self):
        """测试从环境变量解析模型 profile"""
        env = {
            "LLM_PROFILE_DEEPSEEK_PROVIDER": "openai",
            "LLM_PROFILE_DEEPSEEK_MODEL": "deepseek-chat",
            "LLM_PROFILE_DEEPSEEK_BASE_URL": "https://api.deepseek.com/v1",
            "LLM_PROFILE_DEEPSEEK_TEMPERATURE": "0.5",
        }
        with patch.dict(os.environ, env):
            from src.config.settings import _parse_model_profiles

            profiles = _parse_model_profiles()
            assert "deepseek" in profiles
            assert profiles["deepseek"].model == "deepseek-chat"
            assert profiles["deepseek"].base_url == "https://api.deepseek.com/v1"
            assert profiles["deepseek"].temperature == 0.5


class TestBaseAgentModelProfile:
    """测试 BaseAgent 的 model_profile 属性"""

    def test_default_no_profile(self):
        """默认不指定 profile"""

        class DummyAgent(BaseAgent):
            async def execute(self, input_data):
                return {}

        agent = DummyAgent(name="test")
        assert agent.model_profile is None

    def test_explicit_profile(self):
        """显式指定 profile"""

        class DummyAgent(BaseAgent):
            async def execute(self, input_data):
                return {}

        agent = DummyAgent(name="test", model_profile="deepseek")
        assert agent.model_profile == "deepseek"

    def test_repr_with_profile(self):
        """repr 包含 profile 信息"""

        class DummyAgent(BaseAgent):
            async def execute(self, input_data):
                return {}

        agent = DummyAgent(name="test", model_profile="deepseek")
        assert "profile=deepseek" in repr(agent)


class TestOrchestratorMultiModel:
    """测试编排器多模型支持"""

    def test_register_agent_with_model(self):
        """测试显式注册 Agent 并指定模型"""
        orchestrator = Orchestrator()
        agent = CoderAgent()
        orchestrator.register_agent_with_model(agent, "deepseek")
        assert agent.model_profile == "deepseek"
        assert "coder" in orchestrator.list_agents()

    def test_get_agent_model_info(self):
        """测试获取 Agent 模型信息"""
        orchestrator = Orchestrator()
        orchestrator.register_agent(CoderAgent(model_profile="deepseek"))
        orchestrator.register_agent(ReviewerAgent(model_profile="sensenova"))

        info = orchestrator.get_agent_model_info()
        assert info["coder"] == "deepseek"
        assert info["reviewer"] == "sensenova"

    @pytest.mark.asyncio
    async def test_orchestrator_execute_records_models(self):
        """测试编排结果包含模型信息"""
        orchestrator = Orchestrator()
        orchestrator.register_agent(CoderAgent())
        orchestrator.register_agent(ReviewerAgent())

        # Mock call_llm to avoid real API calls
        with patch("src.agents.orchestrator.call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '["coder"]'

            # Mock the coder agent's execute
            coder = orchestrator.get_agent("coder")
            coder.execute = AsyncMock(return_value={"generated_code": "x=1", "status": "completed"})

            result = await orchestrator.execute({"task": "这是一个复杂的代码重构任务需要多人协作完成"})
            assert "agent_models" in result


def _make_mock_llm(response: str = "test response"):
    """创建一个模拟的 LLM 实例"""
    mock_llm = MagicMock()

    async def mock_astream(messages):
        chunk = MagicMock()
        chunk.content = response
        yield chunk

    mock_llm.astream = mock_astream
    return mock_llm


class TestCallLlmWithProfile:
    """测试 call_llm 的 profile 参数"""

    def setup_method(self):
        reset_llm()

    @pytest.mark.asyncio
    async def test_call_llm_default_profile(self):
        """测试默认 profile（None）使用全局配置"""
        mock_llm = _make_mock_llm("hello")

        with patch("src.core.llm._get_llm", return_value=mock_llm):
            result = await call_llm(messages=[{"role": "user", "content": "hi"}])
            assert result == "hello"

    @pytest.mark.asyncio
    async def test_call_llm_explicit_profile(self):
        """测试显式 profile 使用指定模型"""
        env = {
            "LLM_PROFILE_TEST_PROVIDER": "openai",
            "LLM_PROFILE_TEST_MODEL": "test-model",
            "LLM_PROFILE_TEST_BASE_URL": "http://test.local/v1",
        }
        with patch.dict(os.environ, env):
            from src.config.settings import _parse_model_profiles

            profiles = _parse_model_profiles()

            mock_llm = _make_mock_llm("test response")

            with patch("src.core.llm.get_settings") as mock_settings:
                mock_settings.return_value.model_profiles = profiles
                mock_settings.return_value.openai.api_key = None
                mock_settings.return_value.anthropic.api_key = None

                with patch("src.core.llm.ChatOpenAI", return_value=mock_llm) as mock_cls:
                    result = await call_llm(
                        messages=[{"role": "user", "content": "hi"}],
                        profile_name="test",
                    )
                    assert result == "test response"
                    mock_cls.assert_called_once()
                    call_kwargs = mock_cls.call_args
                    assert call_kwargs[1]["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_call_llm_unknown_profile_raises(self):
        """测试未知 profile 抛出异常"""
        with patch("src.core.llm.get_settings") as mock_settings:
            mock_settings.return_value.model_profiles = {}
            with pytest.raises(RuntimeError, match="LLM call failed"):
                await call_llm(
                    messages=[{"role": "user", "content": "hi"}],
                    profile_name="nonexistent",
                )
