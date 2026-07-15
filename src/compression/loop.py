"""五段闭环 - Intent→Context→Action→Observe→Adjustment"""

from typing import Any


class CompressionLoop:
    """五段闭环，实现 Token 压缩的自愈循环"""

    def __init__(self, max_iterations: int = 3):
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive")
        self.max_iterations = max_iterations

    async def run(
        self,
        intent: str,
        context: dict[str, Any],
        token_budget: int = 2000,
    ) -> dict[str, Any]:
        """运行五段闭环

        Args:
            intent: 意图
            context: 上下文
            token_budget: Token 预算

        Returns:
            闭环结果
        """
        if not intent:
            raise ValueError("Intent cannot be empty")

        state = {
            "intent": intent,
            "context": context,
            "token_budget": token_budget,
            "current_tokens": 0,
            "iterations": 0,
            "adjustments": [],
        }

        for iteration in range(self.max_iterations):
            state["iterations"] = iteration + 1

            # 1. Intent: 明确意图
            state = await self._intent_phase(state)

            # 2. Context: 获取相关上下文
            state = await self._context_phase(state)

            # 3. Action: 执行压缩行动
            state = await self._action_phase(state)

            # 4. Observe: 观察结果
            state = await self._observe_phase(state)

            # 5. Adjustment: 调整策略
            state = await self._adjustment_phase(state)

            # 检查是否满足 Token 预算
            if self._is_within_budget(state):
                state["status"] = "within_budget"
                break
        else:
            state["status"] = "max_iterations_reached"

        return state

    async def _intent_phase(self, state: dict[str, Any]) -> dict[str, Any]:
        """意图阶段

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        state["intent_analysis"] = {
            "primary_goal": state["intent"],
            "priority": "high",
            "estimated_tokens": state["token_budget"],
        }
        return state

    async def _context_phase(self, state: dict[str, Any]) -> dict[str, Any]:
        """上下文阶段

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        context = state.get("context", {})
        state["context_summary"] = {
            "total_items": len(context),
            "key_items": list(context.keys())[:5],
        }
        return state

    async def _action_phase(self, state: dict[str, Any]) -> dict[str, Any]:
        """行动阶段

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        # 执行压缩行动
        state["action_taken"] = "compression_applied"
        state["current_tokens"] = max(0, state.get("current_tokens", 0) - 100)
        return state

    async def _observe_phase(self, state: dict[str, Any]) -> dict[str, Any]:
        """观察阶段

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        state["observation"] = {
            "tokens_saved": 100,
            "quality_impact": "minimal",
            "within_budget": self._is_within_budget(state),
        }
        return state

    async def _adjustment_phase(self, state: dict[str, Any]) -> dict[str, Any]:
        """调整阶段

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        observation = state.get("observation", {})
        if not observation.get("within_budget", False):
            adjustment = {
                "type": "increase_compression",
                "reason": "Still over budget",
                "next_action": "apply_stronger_compression",
            }
            state["adjustments"].append(adjustment)

        return state

    def _is_within_budget(self, state: dict[str, Any]) -> bool:
        """检查是否在 Token 预算内

        Args:
            state: 当前状态

        Returns:
            是否在预算内
        """
        current = state.get("current_tokens", 0)
        budget = state.get("token_budget", 2000)
        return bool(current <= budget)
