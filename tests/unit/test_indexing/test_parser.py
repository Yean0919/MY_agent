"""索引单元测试"""

from src.indexing.ast.parser import ASTParser


class TestASTParser:
    """AST 解析器测试"""

    def test_parse_string(self):
        """测试解析字符串"""
        parser = ASTParser()
        ast = parser.parse_string("def hello(): pass")
        assert ast is not None
