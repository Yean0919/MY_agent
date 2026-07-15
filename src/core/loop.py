"""主循环 - Think-Act-Observe 循环"""

from typing import Any

from src.core.exceptions import LoopError


class AgentLoop:
    """Agent 主循环，实现 Think-Act-Observe 模式"""

    def __init__(self, max_iterations: int = 10):
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        self.max_iterations = max_iterations

    async def run(self, initial_input: dict[str, Any]) -> dict[str, Any]:
        """运行主循环

        Args:
            initial_input: 初始输入

        Returns:
            最终输出

        Raises:
            LoopError: 循环异常
        """
        state = initial_input.copy()
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            try:
                state = await self._step(state, iteration)
            except Exception as e:
                raise LoopError(f"Loop step failed at iteration {iteration}") from e

            if self._is_complete(state):
                break

        return state

    async def _step(self, state: dict[str, Any], iteration: int) -> dict[str, Any]:
        """执行一步循环

        Args:
            state: 当前状态
            iteration: 当前迭代次数

        Returns:
            更新后的状态
        """
        # Think: 思考下一步行动
        thought = self._think(state)
        state["thought"] = thought

        # Act: 执行行动
        action = self._act(state)
        state["action"] = action

        # Observe: 观察结果
        observation = self._observe(state)
        state["observation"] = observation

        return state

    def _think(self, state: dict[str, Any]) -> str:
        """思考下一步行动"""
        return f"Processing iteration with state: {state.get('task', 'unknown')}"

    def _act(self, state: dict[str, Any]) -> str:
        """执行行动"""
        return "executing action"

    def _observe(self, state: dict[str, Any]) -> str:
        """观察结果"""
        return "observed result"

    def _is_complete(self, state: dict[str, Any]) -> bool:
        """检查循环是否完成"""
        return bool(state.get("complete", False))
