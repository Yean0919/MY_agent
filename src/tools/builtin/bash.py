"""Bash 工具 - 执行 shell 命令"""

import subprocess
from typing import Any


class BashTool:
    """Bash 工具，执行 shell 命令"""

    def __init__(self, timeout: int = 30):
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout = timeout

    async def execute(self, command: str, cwd: str | None = None) -> dict[str, Any]:
        """执行命令

        Args:
            command: shell 命令
            cwd: 工作目录

        Returns:
            执行结果
        """
        if not command:
            return {"error": "Command cannot be empty"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=cwd,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {self.timeout}s"}
        except Exception as e:
            return {"error": str(e)}
