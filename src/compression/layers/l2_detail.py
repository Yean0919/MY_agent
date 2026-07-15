"""L2 细节层 - 保留关键细节"""

import re
from typing import Any


class L2Detail:
    """L2 细节层，保留关键细节但压缩冗余"""

    def __init__(self, max_tokens: int = 1000):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self.max_tokens = max_tokens

    async def compress(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """压缩消息保留细节

        Args:
            messages: 消息列表

        Returns:
            压缩后的消息列表
        """
        if not messages:
            return []

        compressed = []
        total_tokens = 0

        for msg in messages:
            # 跳过不重要的消息
            if not self._is_important(msg):
                continue

            # 压缩消息内容
            compressed_msg = self._compress_message(msg)
            msg_tokens = self._estimate_tokens(compressed_msg["content"])

            # 检查 Token 预算
            if total_tokens + msg_tokens > self.max_tokens:
                # 截断最后一条消息
                compressed_msg["content"] = (
                    compressed_msg["content"][: self.max_tokens - total_tokens] + "..."
                )
                compressed.append(compressed_msg)
                break

            compressed.append(compressed_msg)
            total_tokens += msg_tokens

        return compressed

    def _is_important(self, message: dict[str, Any]) -> bool:
        """判断消息是否重要

        Args:
            message: 消息

        Returns:
            是否重要
        """
        role = message.get("role", "")
        content = message.get("content", "")

        # 系统消息总是重要
        if role == "system":
            return True

        # 包含代码的消息重要
        if "```" in content:
            return True

        # 包含错误的消息重要
        if "error" in content.lower() or "exception" in content.lower():
            return True

        # 包含决策的消息重要
        if re.search(r"(?:decided|concluded|determined|decide|conclude)", content, re.IGNORECASE):
            return True

        # 用户消息重要
        if role == "user":
            return True

        # 其他消息根据长度判断
        return len(content) > 100

    def _compress_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """压缩单条消息

        Args:
            message: 消息

        Returns:
            压缩后的消息
        """
        content = message.get("content", "")

        # 移除多余空白
        content = re.sub(r"\s+", " ", content).strip()

        # 截断过长的代码块
        content = re.sub(
            r"(```[\w]*\n)(.{500,}?)(\n```)",
            lambda m: m.group(1) + m.group(2)[:500] + "\n... [truncated] ..." + m.group(3),
            content,
            flags=re.DOTALL,
        )

        return {
            "role": message.get("role", "unknown"),
            "content": content,
        }

    def _estimate_tokens(self, text: str) -> int:
        """估算 Token 数

        Args:
            text: 文本

        Returns:
            估算的 Token 数
        """
        # 简单估算：每个字符约 0.25 Token
        return len(text) // 4
