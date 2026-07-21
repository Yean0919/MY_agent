"""审查专家 Agent"""

from typing import Any

from src.core.agent import BaseAgent
from src.core.llm import call_llm, resolve_agent_profile


class ReviewerAgent(BaseAgent):
    """审查专家，负责代码审查"""

    def __init__(self, model_profile: str | None = None) -> None:
        super().__init__(name="reviewer", description="审查代码质量", model_profile=model_profile)

    def _get_profile(self) -> str | None:
        """获取模型 profile：优先使用显式配置，其次从 settings 自动解析"""
        return self.model_profile or resolve_agent_profile(self.name)

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行代码审查

        Args:
            input_data: 包含 code 字段

        Returns:
            包含 review_result 字段
        """
        code = input_data.get("code", "")

        if not code:
            return {
                "review_result": {
                    "approved": False,
                    "issues": ["No code provided for review"],
                    "suggestions": [],
                    "score": 0,
                },
                "status": "error",
                "message": "No code provided",
            }

        try:
            review_text = await call_llm(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "请审查以下代码，输出 JSON 格式结果，包含字段：\n"
                            "- approved (bool): 是否通过\n"
                            "- issues (list[str]): 发现的问题\n"
                            "- suggestions (list[str]): 改进建议\n"
                            "- score (int 0-100): 质量评分\n\n"
                            f"代码：\n```python\n{code}\n```"
                        ),
                    }
                ],
                system_prompt="你是一个严格的代码审查专家，关注正确性、性能、安全性和可维护性。只输出 JSON，不要其他内容。",
                profile_name=self._get_profile(),
            )
            # 尝试解析 JSON，失败则返回原始文本
            import json

            try:
                review_result = json.loads(review_text)
            except json.JSONDecodeError:
                review_result = {
                    "approved": False,
                    "issues": ["Failed to parse review result"],
                    "suggestions": [],
                    "score": 0,
                    "raw_review": review_text,
                }
            return {
                "review_result": review_result,
                "status": "completed",
            }
        except RuntimeError as e:
            return {
                "review_result": {
                    "approved": False,
                    "issues": [str(e)],
                    "suggestions": [],
                    "score": 0,
                },
                "status": "error",
                "message": str(e),
            }
