"""Skill 懒加载器 - 读取 SKILL.md"""

import re
from pathlib import Path
from typing import Any


class SkillLoader:
    """Skill 懒加载器，按需加载 SKILL.md"""

    def __init__(self) -> None:
        self._loaded_skills: dict[str, dict[str, Any]] = {}

    def load_skill(self, skill_path: str | Path) -> dict[str, Any]:
        """加载 Skill

        Args:
            skill_path: Skill 目录路径

        Returns:
            Skill 信息

        Raises:
            FileNotFoundError: SKILL.md 不存在
        """
        path = Path(skill_path)
        skill_file = path / "SKILL.md"

        if not skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found at {skill_file}")

        # 读取 SKILL.md
        content = skill_file.read_text(encoding="utf-8")

        # 解析 Skill 信息
        skill_info = self._parse_skill_md(content)
        skill_info["path"] = str(path)
        skill_info["scripts_dir"] = str(path / "scripts")

        # 缓存
        self._loaded_skills[skill_info["name"]] = skill_info

        return skill_info

    def get_loaded_skill(self, name: str) -> dict[str, Any] | None:
        """获取已加载的 Skill

        Args:
            name: Skill 名称

        Returns:
            Skill 信息或 None
        """
        return self._loaded_skills.get(name)

    def list_loaded_skills(self) -> list[dict[str, Any]]:
        """列出所有已加载的 Skill

        Returns:
            Skill 信息列表
        """
        return list(self._loaded_skills.values())

    def _parse_skill_md(self, content: str) -> dict[str, Any]:
        """解析 SKILL.md 内容

        Args:
            content: SKILL.md 内容

        Returns:
            Skill 信息字典
        """
        skill_info = {
            "name": "unknown",
            "description": "",
            "version": "1.0.0",
        }

        # 提取名称
        name_match = re.search(r"#\s*名称\s*\n\s*(.+)", content)
        if name_match:
            skill_info["name"] = name_match.group(1).strip()

        # 提取描述
        desc_match = re.search(r"#\s*描述\s*\n\s*(.+)", content)
        if desc_match:
            skill_info["description"] = desc_match.group(1).strip()

        # 提取版本
        version_match = re.search(r"#\s*版本\s*\n\s*(.+)", content)
        if version_match:
            skill_info["version"] = version_match.group(1).strip()

        # 提取使用方法
        usage_match = re.search(r"#\s*使用方法\s*\n\s*```.*?\n(.*?)```", content, re.DOTALL)
        if usage_match:
            skill_info["usage"] = usage_match.group(1).strip()

        # 提取参数
        params = re.findall(r"- `(.+?)`:\s*(.+)", content)
        if params:
            skill_info["parameters"] = [{"name": p[0], "description": p[1]} for p in params]  # type: ignore[assignment]

        return skill_info
