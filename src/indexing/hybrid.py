"""双引擎融合 - AST + LSP 混合索引"""

from typing import Any

from src.indexing.ast.parser import ASTParser
from src.indexing.ast.symbols import SymbolExtractor
from src.indexing.lsp.client import LSPClient
from src.indexing.lsp.features import LSPFeatures


class HybridIndexer:
    """双引擎融合索引器，结合 AST 和 LSP 的优势"""

    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.ast_parser = ASTParser()
        self.symbol_extractor = SymbolExtractor(self.ast_parser)
        self.lsp_client = LSPClient(workspace_path)
        self.lsp_features = LSPFeatures(self.lsp_client)

    async def initialize(self) -> None:
        """初始化双引擎"""
        await self.lsp_client.initialize()

    async def index_file(self, file_path: str) -> dict[str, Any]:
        """索引文件

        Args:
            file_path: 文件路径

        Returns:
            索引结果
        """
        # AST 快速过滤
        ast_symbols = self.symbol_extractor.extract_symbols(file_path)

        # LSP 精确确认（可选）
        lsp_symbols = []
        try:  # noqa: SIM105
            lsp_symbols = await self.lsp_features.get_document_symbols(file_path)
        except Exception:
            # LSP 不可用时，只使用 AST 结果
            pass

        return {
            "file_path": file_path,
            "ast_symbols": ast_symbols,
            "lsp_symbols": lsp_symbols,
            "total_symbols": len(ast_symbols) + len(lsp_symbols),
        }

    async def search(self, query: str, symbol_type: str | None = None) -> list[dict[str, Any]]:
        """搜索符号

        Args:
            query: 查询文本
            symbol_type: 符号类型过滤

        Returns:
            搜索结果
        """
        results = []

        # AST 搜索
        # TODO: 实现 AST 搜索

        # LSP 搜索
        lsp_results = await self.lsp_features.find_symbol(query, symbol_type)
        results.extend(lsp_results)

        return results

    async def get_symbol_info(self, file_path: str, line: int, column: int) -> dict[str, Any]:
        """获取符号信息

        Args:
            file_path: 文件路径
            line: 行号
            column: 列号

        Returns:
            符号信息
        """
        # 获取定义
        definitions = await self.lsp_client.get_definition(file_path, line, column)

        # 获取类型信息
        type_info = await self.lsp_features.get_type_info(file_path, line, column)

        return {
            "definitions": definitions,
            "type_info": type_info,
        }
