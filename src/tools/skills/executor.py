"""Skill 执行器"""

import subprocess
from pathlib import Path
from typing import Any


class SkillExecutor:
    """Skill 执行器，执行 Skill 中的脚本"""

    def __init__(self, timeout: int = 30):
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout = timeout

    async def execute(
        self,
        skill: dict[str, Any],
        script_name: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """执行 Skill 脚本

        Args:
            skill: Skill 信息
            script_name: 脚本名称
            args: 参数
            env: 环境变量

        Returns:
            执行结果
        """
        scripts_dir = Path(skill.get("scripts_dir", ""))
        script_path = scripts_dir / script_name

        if not script_path.exists():
            return {"error": f"Script not found: {script_path}"}

        # 执行脚本
        try:
            result = subprocess.run(
                ["python", str(script_path)] + (args or []),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=env,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Script timed out after {self.timeout}s"}
        except Exception as e:
            return {"error": str(e)}
