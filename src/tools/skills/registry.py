"""Skill 注册表"""

from pathlib import Path
from typing import Any

from src.tools.skills.loader import SkillLoader


class SkillRegistry:
    """Skill 注册表，管理所有可用 Skill"""

    def __init__(self, skill_dirs: list[str] | None = None):
        self.skill_dirs = skill_dirs or ["./skills"]
        self.loader = SkillLoader()
        self._skills: dict[str, dict[str, Any]] = {}

    def scan(self) -> None:
        """扫描 Skill 目录"""
        for skill_dir in self.skill_dirs:
            path = Path(skill_dir)
            if not path.exists():
                continue

            for skill_path in path.iterdir():
                if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                    try:
                        skill = self.loader.load_skill(skill_path)
                        self._skills[skill["name"]] = skill
                    except Exception:
                        # 跳过加载失败的 Skill
                        continue

    def register(self, skill: dict[str, Any]) -> None:
        """注册 Skill

        Args:
            skill: Skill 信息
        """
        if "name" not in skill:
            raise ValueError("Skill must have 'name' field")
        self._skills[skill["name"]] = skill

    def unregister(self, name: str) -> None:
        """注销 Skill

        Args:
            name: Skill 名称
        """
        self._skills.pop(name, None)

    def get(self, name: str) -> dict[str, Any] | None:
        """获取 Skill

        Args:
            name: Skill 名称

        Returns:
            Skill 信息或 None
        """
        return self._skills.get(name)

    def list(self) -> list[dict[str, Any]]:
        """列出所有 Skill

        Returns:
            Skill 列表
        """
        return list(self._skills.values())

    def count(self) -> int:
        """获取 Skill 数量

        Returns:
            Skill 数量
        """
        return len(self._skills)
