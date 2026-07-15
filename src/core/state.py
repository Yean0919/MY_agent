"""全局状态定义"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AgentState:
    """Agent 全局状态"""

    # 会话信息
    session_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 当前任务
    task: str = ""
    intent: str = ""

    # 上下文
    context: dict[str, Any] = field(default_factory=dict)

    # 消息历史
    messages: list[dict[str, Any]] = field(default_factory=list)

    # 工具调用结果
    tool_results: list[dict[str, Any]] = field(default_factory=list)

    # 记忆引用
    memory_references: list[str] = field(default_factory=list)

    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)

    # 循环状态
    thought: str = ""
    action: str = ""
    observation: str = ""
    complete: bool = False

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "task": self.task,
            "intent": self.intent,
            "context": self.context,
            "messages": self.messages,
            "tool_results": self.tool_results,
            "memory_references": self.memory_references,
            "metadata": self.metadata,
            "thought": self.thought,
            "action": self.action,
            "observation": self.observation,
            "complete": self.complete,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentState":
        """从字典创建"""
        data = data.copy()
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
