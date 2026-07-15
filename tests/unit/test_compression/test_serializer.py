"""压缩单元测试"""

from src.compression.serializer import SessionSerializer
from src.core.state import AgentState


class TestSessionSerializer:
    """序列化器测试"""

    def test_serialize_deserialize(self):
        """测试序列化/反序列化"""
        serializer = SessionSerializer()
        state = AgentState(session_id="test")
        data = serializer.serialize(state)
        restored = serializer.deserialize(data)
        assert restored.session_id == "test"
