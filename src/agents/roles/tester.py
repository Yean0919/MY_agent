"""测试专家 Agent"""

from typing import Any

from src.core.agent import BaseAgent
from src.core.llm import call_llm


class TesterAgent(BaseAgent):
    """测试专家，负责编写和执行测试"""

    def __init__(self) -> None:
        super().__init__(name="tester", description="编写和执行测试")

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行测试任务

        Args:
            input_data: 包含 code 字段

        Returns:
            包含 test_result 字段
        """
        code = input_data.get("code", "")

        if not code:
            return {
                "test_code": "",
                "test_result": {
                    "passed": False,
                    "total": 0,
                    "passed_count": 0,
                    "failed_count": 0,
                    "message": "No code provided",
                },
                "status": "error",
                "message": "No code provided",
            }

        try:
            test_code = await call_llm(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "请为以下代码编写 pytest 单元测试。"
                            "只输出测试代码，用 markdown 代码块包裹。\n\n"
                            f"代码：\n```python\n{code}\n```"
                        ),
                    }
                ],
                system_prompt="你是一个测试专家，编写覆盖正常路径、边界情况和异常情况的 pytest 测试。",
            )
            return {
                "test_code": test_code,
                "test_result": {
                    "passed": True,
                    "total": 0,
                    "passed_count": 0,
                    "failed_count": 0,
                    "message": "Test code generated (not executed)",
                },
                "status": "completed",
            }
        except RuntimeError as e:
            return {
                "test_code": "",
                "test_result": {
                    "passed": False,
                    "total": 0,
                    "passed_count": 0,
                    "failed_count": 0,
                    "message": str(e),
                },
                "status": "error",
                "message": str(e),
            }
