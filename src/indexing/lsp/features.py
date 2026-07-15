"""LSP 功能封装"""

from typing import Any

from src.indexing.lsp.client import LSPClient


class LSPFeatures:
    """LSP 功能封装"""

    def __init__(self, client: LSPClient):
        self.client = client

    async def find_symbol(self, query: str, symbol_type: str | None = None) -> list[dict[str, Any]]:
        """查找符号

        Args:
            query: 查询文本
            symbol_type: 符号类型过滤

        Returns:
            符号列表
        """
        # TODO: 实现真实的 LSP 符号查找
        # 使用 workspace/symbol 请求
        return [
            {
                "name": query,
                "type": symbol_type or "unknown",
                "location": {"file": "unknown", "line": 0, "column": 0},
            }
        ]

    async def get_type_info(self, file_path: str, line: int, column: int) -> dict[str, Any] | None:
        """获取类型信息

        Args:
            file_path: 文件路径
            line: 行号
            column: 列号

        Returns:
            类型信息
        """
        hover = await self.client.get_hover(file_path, line, column)
        if hover:
            return {
                "type": hover.get("type", "unknown"),
                "documentation": hover.get("documentation", ""),
            }
        return None

    async def get_completions(self, file_path: str, line: int, column: int) -> list[dict[str, Any]]:
        """获取补全建议

        Args:
            file_path: 文件路径
            line: 行号
            column: 列号

        Returns:
            补全建议列表
        """
        return await self.client.get_completion(file_path, line, column)

    async def get_document_symbols(self, file_path: str) -> list[dict[str, Any]]:
        """获取文档符号

        Args:
            file_path: 文件路径

        Returns:
            符号列表
        """
        # TODO: 实现真实的 LSP 文档符号查询
        return []

    async def get_workspace_symbols(self, query: str) -> list[dict[str, Any]]:
        """获取工作区符号

        Args:
            query: 查询文本

        Returns:
            符号列表
        """
        return await self.find_symbol(query)
