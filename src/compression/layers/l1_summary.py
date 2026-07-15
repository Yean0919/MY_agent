"""L1 摘要层 - 最高级别压缩"""

import re
from typing import Any


class L1Summary:
    """L1 摘要层，将消息压缩为简短摘要"""

    def __init__(self, max_tokens: int = 200):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self.max_tokens = max_tokens

    async def compress(self, messages: list[dict[str, Any]]) -> str:
        """压缩消息为摘要

        Args:
            messages: 消息列表

        Returns:
            摘要字符串
        """
        if not messages:
            return ""

        # 提取关键信息
        key_points = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # 提取代码块
            code_count = len(re.findall(r"```", content)) // 2
            if code_count > 0:
                key_points.append(f"[{role}] Generated {code_count} code blocks")

            # 提取错误
            errors = re.findall(r"Error: (.+)", content)
            if errors:
                key_points.append(f"[{role}] Errors: {', '.join(errors[:2])}")

            # 提取关键决策
            decisions = re.findall(
                r"(?:decided|concluded|determined): (.+)", content, re.IGNORECASE
            )
            for decision in decisions[:2]:
                key_points.append(f"[{role}] {decision}")

        # 生成摘要
        summary = f"Session Summary ({len(messages)} messages):\n"
        for point in key_points[:10]:  # 限制摘要长度
            summary += f"- {point}\n"

        # 截断到最大 Token 数（近似）
        if len(summary) > self.max_tokens * 4:  # 假设每个 Token 约 4 字符
            summary = summary[: self.max_tokens * 4] + "..."

        return summary

    async def decompress(self, summary: str) -> list[dict[str, Any]]:
        """从摘要恢复消息（近似）

        Args:
            summary: 摘要字符串

        Returns:
            恢复的消息列表
        """
        if not summary:
            return []

        return [
            {
                "role": "system",
                "content": f"[Compressed Summary]\n{summary}",
            }
        ]
