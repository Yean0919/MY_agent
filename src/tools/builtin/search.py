"""Search 工具 - 搜索文件"""

from pathlib import Path
from typing import Any


class SearchTool:
    """Search 工具，在文件中搜索文本"""

    async def execute(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        context: int = 0,
    ) -> dict[str, Any]:
        """搜索文件

        Args:
            pattern: 搜索模式
            path: 搜索路径
            file_pattern: 文件模式
            context: 上下文行数

        Returns:
            搜索结果
        """
        if not pattern:
            return {"error": "Pattern cannot be empty"}

        search_path = Path(path)
        results = []

        try:
            for file_path in search_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                # 跳过隐藏文件和常见非文本文件
                if file_path.name.startswith("."):
                    continue
                if file_path.suffix in (".pyc", ".pyo", ".so", ".dll", ".exe"):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")

                    for i, line in enumerate(lines):
                        if pattern in line:
                            # 添加上下文
                            start = max(0, i - context)
                            end = min(len(lines), i + context + 1)
                            context_lines = lines[start:end]

                            results.append(
                                {
                                    "file": str(file_path),
                                    "line": i + 1,
                                    "content": "\n".join(context_lines),
                                }
                            )
                except Exception:
                    # 跳过无法读取的文件
                    continue
        except Exception as e:
            return {"error": str(e)}

        return {"results": results, "count": len(results)}
