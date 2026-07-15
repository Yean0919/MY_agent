"""记忆单元测试"""

from src.memory.short_term.session_state import SessionState


class TestSessionState:
    """会话状态测试"""

    def test_update(self):
        """测试更新"""
        session = SessionState("test_session")
        session.update({"task": "test_task"})
        assert session.state.task == "test_task"

    def test_to_dict(self):
        """测试转换为字典"""
        session = SessionState("test_session")
        data = session.to_dict()
        assert data["session_id"] == "test_session"
