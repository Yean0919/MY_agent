"""Maker-Checker 辩论机制"""

from typing import Any

from src.core.agent import BaseAgent
from src.core.exceptions import AgentError


class DebateMechanism:
    """Maker-Checker 辩论机制，用于提高输出质量"""

    def __init__(self, maker: BaseAgent, checker: BaseAgent, max_rounds: int = 3):
        if max_rounds <= 0:
            raise ValueError("max_rounds must be positive")
        self.maker = maker
        self.checker = checker
        self.max_rounds = max_rounds

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行辩论

        Args:
            input_data: 输入数据

        Returns:
            辩论结果

        Raises:
            AgentError: 辩论错误
        """
        if not input_data:
            raise AgentError("Input data cannot be empty")

        result = None
        review_history = []

        for round_num in range(self.max_rounds):
            # Maker 生成
            try:
                result = await self.maker.execute(input_data)
            except Exception as e:
                raise AgentError(f"Maker execution failed: {e}") from e

            # Checker 审查
            try:
                review = await self.checker.execute({"code": result})
            except Exception as e:
                raise AgentError(f"Checker execution failed: {e}") from e

            review_history.append(
                {
                    "round": round_num + 1,
                    "review": review,
                }
            )

            # 如果通过，返回结果
            if self._is_approved(review):
                return {
                    "result": result,
                    "rounds": round_num + 1,
                    "review_history": review_history,
                    "status": "approved",
                }

            # 否则，将审查意见反馈给 Maker
            input_data["feedback"] = review

        # 达到最大轮数，返回最后结果
        return {
            "result": result,
            "rounds": self.max_rounds,
            "review_history": review_history,
            "status": "max_rounds_reached",
        }

    def _is_approved(self, review: dict[str, Any]) -> bool:
        """检查是否通过审查

        Args:
            review: 审查结果

        Returns:
            是否通过
        """
        return bool(review.get("review_result", {}).get("approved", False))
