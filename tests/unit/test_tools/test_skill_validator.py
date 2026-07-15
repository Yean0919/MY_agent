"""Skill 单元测试"""

from src.tools.skills.validator import SkillValidator


class TestSkillValidator:
    """Skill 验证器测试"""

    def test_validate_valid_skill(self, tmp_path):
        """测试验证有效 Skill"""
        # 创建测试 Skill
        skill_dir = tmp_path / "test_skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """
# Name
test_skill

# Description
Test Skill

# Version
1.0.0
""",
            encoding="utf-8",
        )
        (skill_dir / "scripts").mkdir()

        # 验证
        validator = SkillValidator()
        result = validator.validate(str(skill_dir))

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_missing_field(self, tmp_path):
        """测试验证缺少字段"""
        # 创建测试 Skill（缺少版本）
        skill_dir = tmp_path / "test_skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """
# Name
test_skill

# Description
Test Skill
""",
            encoding="utf-8",
        )

        # 验证
        validator = SkillValidator()
        result = validator.validate(str(skill_dir))

        assert result["valid"] is False
        assert any("Version" in error for error in result["errors"])
