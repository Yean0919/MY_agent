"""Edit 工具单元测试"""

import pytest

from src.tools.builtin.edit import EditTool


class TestEditTool:
    """Edit 工具测试"""

    @pytest.mark.asyncio
    async def test_edit_file(self, tmp_path):
        """测试编辑文件"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")

        # 编辑文件
        tool = EditTool()
        result = await tool.execute(str(test_file), "world", "Python")

        assert result["success"] is True
        assert test_file.read_text() == "Hello, Python!"

    @pytest.mark.asyncio
    async def test_edit_file_not_found(self):
        """测试编辑不存在的文件"""
        tool = EditTool()
        result = await tool.execute("/nonexistent/file.txt", "old", "new")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_edit_text_not_found(self, tmp_path):
        """测试编辑文本不存在"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")

        tool = EditTool()
        result = await tool.execute(str(test_file), "notfound", "new")

        assert "error" in result
