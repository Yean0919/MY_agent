"""Write 工具 - 写入文件"""

from pathlib import Path
from typing import Any


class WriteTool:
    """Write 工具，写入文件内容"""

    async def execute(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> dict[str, Any]:
        """写入文件

        Args:
            file_path: 文件路径
            content: 内容
            encoding: 编码
            create_dirs: 是否创建目录

        Returns:
            写入结果
        """
        path = Path(file_path)

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        try:
            path.write_text(content, encoding=encoding)
            return {
                "success": True,
                "path": str(path),
                "size": path.stat().st_size,
            }
        except Exception as e:
            return {"error": str(e)}
