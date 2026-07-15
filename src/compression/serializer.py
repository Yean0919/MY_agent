"""SessionState 序列化"""

import json
from pathlib import Path

from src.core.state import AgentState


class SessionSerializer:
    """SessionState 序列化器"""

    def __init__(self, storage_path: str = "./data/sessions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def serialize(self, state: AgentState) -> str:
        """序列化状态

        Args:
            state: Agent 状态

        Returns:
            JSON 字符串
        """
        return json.dumps(state.to_dict(), ensure_ascii=False, indent=2)

    def deserialize(self, data: str) -> AgentState:
        """反序列化状态

        Args:
            data: JSON 字符串

        Returns:
            Agent 状态
        """
        if not data:
            raise ValueError("Data cannot be empty")
        return AgentState.from_dict(json.loads(data))

    async def save(self, session_id: str, state: AgentState) -> None:
        """保存状态

        Args:
            session_id: 会话 ID
            state: Agent 状态
        """
        if not session_id:
            raise ValueError("Session ID cannot be empty")

        file_path = self.storage_path / f"{session_id}.json"
        file_path.write_text(self.serialize(state), encoding="utf-8")

    async def load(self, session_id: str) -> AgentState | None:
        """加载状态

        Args:
            session_id: 会话 ID

        Returns:
            Agent 状态或 None
        """
        file_path = self.storage_path / f"{session_id}.json"
        if not file_path.exists():
            return None
        return self.deserialize(file_path.read_text(encoding="utf-8"))

    async def delete(self, session_id: str) -> None:
        """删除状态

        Args:
            session_id: 会话 ID
        """
        file_path = self.storage_path / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()

    async def list_sessions(self) -> list[str]:
        """列出所有会话

        Returns:
            会话 ID 列表
        """
        sessions = []
        for file_path in self.storage_path.glob("*.json"):
            sessions.append(file_path.stem)
        return sorted(sessions)
