"""上下文 Token 注入 - 将代码上下文注入到 Agent 提示中"""

from pathlib import Path

from src.indexing.hybrid import HybridIndexer


class ContextInjector:
    """上下文注入器，根据 Token 预算注入相关代码上下文"""

    def __init__(self, indexer: HybridIndexer):
        self.indexer = indexer

    async def get_context(
        self,
        file_path: str,
        line: int,
        token_budget: int = 1000,
    ) -> str:
        """获取上下文

        Args:
            file_path: 文件路径
            line: 当前行号
            token_budget: Token 预算

        Returns:
            上下文字符串
        """
        path = Path(file_path)
        if not path.exists():
            return ""

        # 读取文件内容
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # 获取当前行周围的内容
        context_lines = []
        start = max(0, line - 10)
        end = min(len(lines), line + 10)

        for i in range(start, end):
            context_lines.append(f"{i + 1}: {lines[i]}")

        context = "\n".join(context_lines)

        # 根据 Token 预算裁剪
        if len(context) > token_budget * 4:  # 假设每个 Token 约 4 字符
            context = context[: token_budget * 4] + "\n... [truncated]"

        return context

    async def inject_context(
        self,
        prompt: str,
        file_path: str,
        line: int,
        token_budget: int = 1000,
    ) -> str:
        """注入上下文到提示

        Args:
            prompt: 原始提示
            file_path: 文件路径
            line: 当前行号
            token_budget: Token 预算

        Returns:
            注入上下文后的提示
        """
        context = await self.get_context(file_path, line, token_budget)

        if context:
            return f"""{prompt}

## 相关代码上下文
```python
{context}
```
"""
        return prompt

    async def get_symbol_context(
        self,
        file_path: str,
        line: int,
        column: int,
    ) -> str:
        """获取符号上下文

        Args:
            file_path: 文件路径
            line: 行号
            column: 列号

        Returns:
            符号上下文字符串
        """
        symbol_info = await self.indexer.get_symbol_info(file_path, line, column)

        context_parts = []

        # 添加定义信息
        definitions = symbol_info.get("definitions", [])
        if definitions:
            context_parts.append("## 定义")
            for defn in definitions:
                context_parts.append(
                    f"- {defn.get('symbol', 'unknown')} at {defn.get('file', 'unknown')}:{defn.get('line', 0)}"
                )

        # 添加类型信息
        type_info = symbol_info.get("type_info")
        if type_info:
            context_parts.append("## 类型信息")
            context_parts.append(f"- Type: {type_info.get('type', 'unknown')}")
            if type_info.get("documentation"):
                context_parts.append(f"- Documentation: {type_info['documentation']}")

        return "\n".join(context_parts) if context_parts else ""
