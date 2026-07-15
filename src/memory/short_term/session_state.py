"""会话状态管理"""

from datetime import datetime
from typing import Any

from src.core.state import AgentState


class SessionState:
    """会话状态管理"""

    def __init__(self, session_id: str):
        if not session_id:
            raise ValueError("Session ID cannot be empty")
        self.session_id = session_id
        self.state = AgentState(session_id=session_id)
        self._history: list[AgentState] = []

    def update(self, updates: dict[str, Any]) -> None:
        """更新状态

        Args:
            updates: 更新字典
        """
        # 保存当前状态到历史
        self._history.append(AgentState.from_dict(self.state.to_dict()))

        # 更新状态
        for key, value in updates.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)

        self.state.updated_at = datetime.now()

    def get_history(self) -> list[AgentState]:
        """获取状态历史

        Returns:
            状态历史列表
        """
        return self._history.copy()

    def get_history_count(self) -> int:
        """获取历史记录数量

        Returns:
            历史记录数量
        """
        return len(self._history)

    def clear_history(self) -> None:
        """清空历史记录"""
        self._history.clear()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典

        Returns:
            字典
        """
        return {
            "session_id": self.session_id,
            "state": self.state.to_dict(),
            "history_count": len(self._history),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        """从字典创建

        Args:
            data: 字典

        Returns:
            SessionState 实例
        """
        session = cls(data["session_id"])
        session.state = AgentState.from_dict(data["state"])
        return session
