"""工具单元测试"""

import pytest

from src.tools.builtin.read import ReadTool


class TestReadTool:
    """Read 工具测试"""

    @pytest.mark.asyncio
    async def test_read_file(self, tmp_path):
        """测试读取文件"""
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")

        # 读取文件
        tool = ReadTool()
        result = await tool.execute(str(test_file))

        assert "content" in result
        assert result["content"] == "Hello, world!"
