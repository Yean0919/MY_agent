"""tree-sitter AST 解析器"""

from pathlib import Path
from typing import Any, cast

import tree_sitter_python as tspython
from tree_sitter import Language, Parser


class ASTParser:
    """使用 tree-sitter 解析 Python 代码的 AST"""

    def __init__(self) -> None:
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)

    def parse_file(self, file_path: str | Path) -> dict[str, Any]:
        """解析文件

        Args:
            file_path: 文件路径

        Returns:
            AST 字典

        Raises:
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        source_code = path.read_text(encoding="utf-8")
        tree = self.parser.parse(bytes(source_code, "utf-8"))
        return self._tree_to_dict(tree.root_node)

    def parse_string(self, source_code: str) -> dict[str, Any]:
        """解析字符串

        Args:
            source_code: 源代码字符串

        Returns:
            AST 字典
        """
        if not source_code:
            return {"type": "empty", "children": []}

        tree = self.parser.parse(bytes(source_code, "utf-8"))
        return self._tree_to_dict(tree.root_node)

    def _tree_to_dict(self, node: Any) -> dict[str, Any]:
        """将树节点转换为字典

        Args:
            node: 树节点

        Returns:
            字典
        """
        node_dict = {
            "type": node.type,
            "start_point": list(node.start_point),
            "end_point": list(node.end_point),
            "children": [],
        }

        for child in node.children:
            node_dict["children"].append(self._tree_to_dict(child))

        return node_dict

    def get_symbols(self, ast: dict[str, Any]) -> list[dict[str, Any]]:
        """从 AST 提取符号

        Args:
            ast: AST 字典

        Returns:
            符号列表
        """
        symbols: list[dict[str, Any]] = []
        self._extract_symbols(ast, symbols)
        return symbols

    def _extract_symbols(self, node: dict[str, Any], symbols: list[dict[str, Any]]) -> None:
        """递归提取符号

        Args:
            node: 节点
            symbols: 符号列表
        """
        node_type = node.get("type", "")

        if node_type == "function_definition":
            name_node = self._find_child(node, "identifier")
            if name_node:
                symbols.append(
                    {
                        "type": "function",
                        "name": name_node.get("text", "unknown"),
                        "line": node.get("start_point", [0])[0],
                    }
                )

        elif node_type == "class_definition":
            name_node = self._find_child(node, "identifier")
            if name_node:
                symbols.append(
                    {
                        "type": "class",
                        "name": name_node.get("text", "unknown"),
                        "line": node.get("start_point", [0])[0],
                    }
                )

        for child in node.get("children", []):
            self._extract_symbols(child, symbols)

    def _find_child(self, node: dict[str, Any], child_type: str) -> dict[str, Any] | None:
        """查找子节点

        Args:
            node: 节点
            child_type: 子节点类型

        Returns:
            子节点或 None
        """
        for child in node.get("children", []):
            if child.get("type") == child_type:
                return cast(dict[str, Any], child)
        return None
