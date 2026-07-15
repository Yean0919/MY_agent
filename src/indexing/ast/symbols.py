"""符号提取 - 从 AST 中提取函数、类、变量等符号"""

from typing import Any

from src.indexing.ast.parser import ASTParser


class SymbolExtractor:
    """从 AST 中提取符号"""

    def __init__(self, parser: ASTParser):
        self.parser = parser

    def extract_symbols(self, file_path: str) -> list[dict[str, Any]]:
        """提取文件中的所有符号

        Args:
            file_path: 文件路径

        Returns:
            符号列表
        """
        ast = self.parser.parse_file(file_path)
        return self.parser.get_symbols(ast)

    def extract_symbols_from_string(self, source_code: str) -> list[dict[str, Any]]:
        """从字符串提取符号

        Args:
            source_code: 源代码

        Returns:
            符号列表
        """
        ast = self.parser.parse_string(source_code)
        return self.parser.get_symbols(ast)

    def filter_by_type(
        self, symbols: list[dict[str, Any]], symbol_type: str
    ) -> list[dict[str, Any]]:
        """按类型过滤符号

        Args:
            symbols: 符号列表
            symbol_type: 符号类型

        Returns:
            过滤后的符号列表
        """
        return [s for s in symbols if s.get("type") == symbol_type]

    def search_by_name(self, symbols: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
        """按名称搜索符号

        Args:
            symbols: 符号列表
            name: 名称

        Returns:
            匹配的符号列表
        """
        name_lower = name.lower()
        return [s for s in symbols if name_lower in s.get("name", "").lower()]

    def get_symbol_stats(self, symbols: list[dict[str, Any]]) -> dict[str, Any]:
        """获取符号统计信息

        Args:
            symbols: 符号列表

        Returns:
            统计信息
        """
        stats: dict[str, Any] = {
            "total": len(symbols),
            "by_type": {},
        }

        for symbol in symbols:
            symbol_type = symbol.get("type", "unknown")
            by_type: dict[str, int] = stats["by_type"]
            by_type[symbol_type] = by_type.get(symbol_type, 0) + 1

        return stats
