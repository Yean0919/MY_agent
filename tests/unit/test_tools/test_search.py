"""Search 工具单元测试"""

import pytest

from src.tools.builtin.search import SearchTool


class TestSearchTool:
    """Search 工具测试"""

    @pytest.mark.asyncio
    async def test_search_file(self, tmp_path):
        """测试搜索文件"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    print("Hello, world!")

def goodbye():
    print("Goodbye, world!")
""")

        # 搜索
        tool = SearchTool()
        result = await tool.execute("world", str(tmp_path))

        assert result["count"] == 2
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_search_with_context(self, tmp_path):
        """测试带上下文的搜索"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    print("Hello, world!")
    return True

def goodbye():
    print("Goodbye, world!")
    return False
""")

        # 搜索（带上下文）
        tool = SearchTool()
        result = await tool.execute("world", str(tmp_path), context=1)

        assert result["count"] == 2
        # 检查结果包含上下文
        for r in result["results"]:
            assert "print" in r["content"]
