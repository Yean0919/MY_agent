"""后台 LLM 提炼 - 将短期记忆提炼为长期知识"""

import re
from datetime import datetime
from typing import Any

from src.core.exceptions import MemoryError
from src.memory.long_term.chroma_store import ChromaStore


class MemoryConsolidation:
    """记忆提炼器，后台运行将短期记忆提炼为长期知识"""

    def __init__(self, chroma_store: ChromaStore):
        self.store = chroma_store

    async def consolidate(self, session_states: list[dict[str, Any]]) -> list[str]:
        """提炼会话状态为长期知识

        Args:
            session_states: 会话状态列表

        Returns:
            存储的文档 ID 列表

        Raises:
            MemoryError: 提炼失败
        """
        if not session_states:
            return []

        doc_ids = []
        for state in session_states:
            try:
                knowledge = self._extract_knowledge(state)
                if knowledge:
                    doc_id = await self.store.store(
                        knowledge["content"],
                        knowledge["metadata"],
                    )
                    doc_ids.append(doc_id)
            except Exception as e:
                raise MemoryError(f"Failed to consolidate state: {e}") from e

        return doc_ids

    def _extract_knowledge(self, state: dict[str, Any]) -> dict[str, Any] | None:
        """从状态中提取知识

        Args:
            state: 会话状态

        Returns:
            知识字典或 None
        """
        # 提取任务信息
        task = state.get("task", "")
        if not task:
            return None

        # 提取工具调用结果
        tool_results = state.get("tool_results", [])
        if not tool_results:
            return None

        # 生成知识内容
        content = f"""
# Task: {task}

## Tool Results
"""
        for result in tool_results:
            content += f"- {result.get('tool', 'unknown')}: {result.get('result', '')}\n"

        # 提取关键信息
        key_insights = self._extract_key_insights(state)
        if key_insights:
            content += "\n## Key Insights\n"
            for insight in key_insights:
                content += f"- {insight}\n"

        metadata = {
            "category": "session_summary",
            "tags": ["consolidated", "session"],
            "source": state.get("session_id", ""),
            "created_at": datetime.now().isoformat(),
        }

        return {"content": content, "metadata": metadata}

    def _extract_key_insights(self, state: dict[str, Any]) -> list[str]:
        """提取关键洞察

        Args:
            state: 会话状态

        Returns:
            关键洞察列表
        """
        insights = []

        # 从消息中提取
        messages = state.get("messages", [])
        for msg in messages:
            content = msg.get("content", "")
            # 提取代码块
            code_blocks = re.findall(r"```[\w]*\n(.*?)```", content, re.DOTALL)
            if code_blocks:
                insights.append(f"Generated {len(code_blocks)} code blocks")

            # 提取错误信息
            errors = re.findall(r"Error: (.+)", content)
            if errors:
                insights.append(f"Encountered errors: {', '.join(errors[:3])}")

        return insights
