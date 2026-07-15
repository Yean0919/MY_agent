"""Read 工具 - 读取文件"""

from pathlib import Path
from typing import Any


class ReadTool:
    """Read 工具，读取文件内容"""

    async def execute(self, file_path: str, encoding: str = "utf-8") -> dict[str, Any]:
        """读取文件

        Args:
            file_path: 文件路径
            encoding: 编码

        Returns:
            文件内容
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        if not path.is_file():
            return {"error": f"Not a file: {file_path}"}

        try:
            content = path.read_text(encoding=encoding)
            return {
                "content": content,
                "path": str(path),
                "size": path.stat().st_size,
            }
        except UnicodeDecodeError:
            return {"error": f"Failed to decode file with encoding: {encoding}"}
        except Exception as e:
            return {"error": str(e)}
