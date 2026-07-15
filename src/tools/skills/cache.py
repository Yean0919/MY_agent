"""Skill 缓存 - 缓存已加载的 Skill"""

import hashlib
from pathlib import Path
from typing import Any


class SkillCache:
    """Skill 缓存，避免重复加载"""

    def __init__(self, max_size: int = 100):
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._cache: dict[str, dict[str, Any]] = {}
        self._checksums: dict[str, str] = {}

    def get(self, skill_path: str) -> dict[str, Any] | None:
        """从缓存获取 Skill

        Args:
            skill_path: Skill 路径

        Returns:
            Skill 信息或 None
        """
        return self._cache.get(skill_path)

    def set(self, skill_path: str, skill: dict[str, Any]) -> None:
        """缓存 Skill

        Args:
            skill_path: Skill 路径
            skill: Skill 信息
        """
        # 如果缓存已满，移除最旧的
        if len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            del self._checksums[oldest_key]

        self._cache[skill_path] = skill
        self._checksums[skill_path] = self._compute_checksum(skill_path)

    def is_valid(self, skill_path: str) -> bool:
        """检查缓存是否有效（文件未修改）

        Args:
            skill_path: Skill 路径

        Returns:
            是否有效
        """
        if skill_path not in self._cache:
            return False

        current_checksum = self._compute_checksum(skill_path)
        return self._checksums.get(skill_path) == current_checksum

    def invalidate(self, skill_path: str) -> None:
        """使缓存失效

        Args:
            skill_path: Skill 路径
        """
        self._cache.pop(skill_path, None)
        self._checksums.pop(skill_path, None)

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._checksums.clear()

    def size(self) -> int:
        """获取缓存大小

        Returns:
            缓存大小
        """
        return len(self._cache)

    def _compute_checksum(self, skill_path: str) -> str:
        """计算文件校验和

        Args:
            skill_path: Skill 路径

        Returns:
            校验和
        """
        path = Path(skill_path) / "SKILL.md"
        if not path.exists():
            return ""
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()
