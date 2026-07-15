"""Agent 基类 - 定义 Agent 的基本接口"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Agent 基类，所有 Agent 必须继承此类"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行 Agent 任务

        Args:
            input_data: 输入数据

        Returns:
            输出数据
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
