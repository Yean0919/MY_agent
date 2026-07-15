"""Skill 验证器 - 验证 SKILL.md 格式"""

from pathlib import Path
from typing import Any


class SkillValidator:
    """Skill 验证器，验证 SKILL.md 格式是否正确"""

    REQUIRED_FIELDS = ["Name", "Description", "Version"]

    def validate(self, skill_path: str | Path) -> dict[str, Any]:
        """验证 Skill

        Args:
            skill_path: Skill 目录路径

        Returns:
            验证结果
        """
        path = Path(skill_path)
        skill_file = path / "SKILL.md"

        errors: list[str] = []
        warnings: list[str] = []

        # 检查 SKILL.md 是否存在
        if not skill_file.exists():
            errors.append("SKILL.md not found")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # 读取内容
        content = skill_file.read_text(encoding="utf-8")

        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if f"## {field}" not in content and f"# {field}" not in content:
                errors.append(f"Missing required field: {field}")

        # 检查 scripts 目录
        scripts_dir = path / "scripts"
        if not scripts_dir.exists():
            warnings.append("scripts directory not found")
        elif not any(scripts_dir.iterdir()):
            warnings.append("scripts directory is empty")

        # 检查名称是否有效
        name_match = __import__("re").search(r"#\s*Name\s*\n\s*(.+)", content)
        if name_match:
            name = name_match.group(1).strip()
            if not name or len(name) < 2:
                errors.append("Skill name is too short")
            if not name.replace("_", "").replace("-", "").isalnum():
                warnings.append("Skill name contains special characters")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
