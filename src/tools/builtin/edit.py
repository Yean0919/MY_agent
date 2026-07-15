"""Edit 工具 - 编辑文件"""

from pathlib import Path
from typing import Any


class EditTool:
    """Edit 工具，编辑文件内容"""

    async def execute(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        encoding: str = "utf-8",
    ) -> dict[str, Any]:
        """编辑文件

        Args:
            file_path: 文件路径
            old_string: 要替换的文本
            new_string: 新文本
            encoding: 编码

        Returns:
            编辑结果
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding=encoding)

            if old_string not in content:
                return {"error": f"Text not found: {old_string}"}

            # 替换文本（只替换第一个匹配）
            new_content = content.replace(old_string, new_string, 1)
            path.write_text(new_content, encoding=encoding)

            return {
                "success": True,
                "path": str(path),
                "replacements": 1,
            }
        except Exception as e:
            return {"error": str(e)}
