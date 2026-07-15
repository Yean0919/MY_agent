"""研究专家 Agent"""

from typing import Any

from src.core.agent import BaseAgent
from src.core.llm import call_llm


class ResearcherAgent(BaseAgent):
    """研究专家，负责信息检索和分析"""

    def __init__(self) -> None:
        super().__init__(name="researcher", description="信息检索和分析")

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行研究任务

        Args:
            input_data: 包含 query 字段

        Returns:
            包含 research_result 字段
        """
        query = input_data.get("query", "") or input_data.get("task", "")

        if not query:
            return {
                "research_result": {
                    "query": "",
                    "findings": [],
                    "total_findings": 0,
                    "confidence": 0.0,
                },
                "status": "error",
                "message": "No query provided",
            }

        try:
            research_text = await call_llm(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "请对以下主题进行技术研究和分析，输出 JSON 格式结果，包含字段：\n"
                            "- findings (list): 每项包含 title, summary, relevance(0-1)\n"
                            "- total_findings (int)\n"
                            "- confidence (float 0-1)\n\n"
                            f"研究主题：{query}"
                        ),
                    }
                ],
                system_prompt="你是一个技术研究员，基于你的知识对主题进行深入分析。只输出 JSON，不要其他内容。",
            )
            import json

            try:
                research_result = json.loads(research_text)
            except json.JSONDecodeError:
                research_result = {
                    "query": query,
                    "findings": [
                        {"title": "Research result", "summary": research_text, "relevance": 0.9}
                    ],
                    "total_findings": 1,
                    "confidence": 0.7,
                    "raw_result": research_text,
                }
            return {
                "research_result": research_result,
                "status": "completed",
            }
        except RuntimeError as e:
            return {
                "research_result": {
                    "query": query,
                    "findings": [],
                    "total_findings": 0,
                    "confidence": 0.0,
                },
                "status": "error",
                "message": str(e),
            }
