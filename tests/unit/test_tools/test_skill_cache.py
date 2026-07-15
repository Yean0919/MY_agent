"""Skill 缓存单元测试"""

from src.tools.skills.cache import SkillCache


class TestSkillCache:
    """Skill 缓存测试"""

    def test_set_get(self):
        """测试设置和获取"""
        cache = SkillCache()
        skill = {"name": "test", "description": "test skill"}
        cache.set("/path/to/skill", skill)

        result = cache.get("/path/to/skill")
        assert result == skill

    def test_max_size(self):
        """测试最大缓存大小"""
        cache = SkillCache(max_size=2)
        cache.set("/path1", {"name": "skill1"})
        cache.set("/path2", {"name": "skill2"})
        cache.set("/path3", {"name": "skill3"})  # 应该移除 path1

        assert cache.get("/path1") is None
        assert cache.get("/path2") is not None
        assert cache.get("/path3") is not None

    def test_clear(self):
        """测试清空缓存"""
        cache = SkillCache()
        cache.set("/path1", {"name": "skill1"})
        cache.clear()

        assert cache.get("/path1") is None
