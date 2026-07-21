"""测试生成脚本 - 分析 Python 源码并生成 pytest 测试"""

import argparse
import ast
import sys
from pathlib import Path
from typing import Any


class TestGenerator:
    """从 Python 源码生成 pytest 测试"""

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """分析源文件，提取函数和类信息"""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        functions = []
        classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._extract_func_info(node))
            elif isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(self._extract_func_info(item))
                classes.append({"name": node.name, "methods": methods})

        return {"functions": functions, "classes": classes}

    def _extract_func_info(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict:
        """提取函数信息"""
        args = []
        for arg in node.args.args:
            if arg.arg != "self":
                annotation = ""
                if arg.annotation:
                    annotation = ast.unparse(arg.annotation)
                args.append({"name": arg.arg, "type": annotation})

        return_annotation = ""
        if node.returns:
            return_annotation = ast.unparse(node.returns)

        docstring = ast.get_docstring(node) or ""

        return {
            "name": node.name,
            "args": args,
            "return_type": return_annotation,
            "docstring": docstring,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
        }

    def generate_test(self, func_info: dict, module_name: str) -> str:
        """为单个函数生成测试代码"""
        name = func_info["name"]
        args = func_info["args"]
        is_async = func_info["is_async"]

        lines = []
        lines.append(f"class Test{name.title().replace('_', '')}:")
        lines.append(f'    """{name} 的测试"""')
        lines.append("")

        # 生成正常路径测试
        args_str = ", ".join([self._default_value(a["type"]) for a in args])
        async_prefix = "async " if is_async else ""
        await_prefix = "await " if is_async else ""

        lines.append(f"    @{'' if not is_async else 'pytest.mark.asyncio'}")
        if is_async:
            lines.append("    @pytest.mark.asyncio")
        lines.append(f"    {async_prefix}def test_{name}_basic(self):")
        lines.append(f'        """测试 {name} 的基本功能"""')
        lines.append(f"        result = {await_prefix}{module_name}.{name}({args_str})")
        lines.append("        assert result is not None")
        lines.append("")

        # 生成边界条件测试
        if args:
            lines.append(f"    {async_prefix}def test_{name}_edge_cases(self):")
            lines.append(f'        """测试 {name} 的边界条件"""')
            for arg in args:
                edge_val = self._edge_value(arg["type"])
                lines.append(f"        # 测试 {arg['name']} 的边界值")
                lines.append(f"        # result = {await_prefix}{module_name}.{name}({edge_val})")
            lines.append("")

        # 生成异常测试
        lines.append(f"    {async_prefix}def test_{name}_invalid_input(self):")
        lines.append(f'        """测试 {name} 的异常处理"""')
        lines.append("        with pytest.raises(Exception):")
        lines.append(f"            {await_prefix}{module_name}.{name}(None)")
        lines.append("")

        return "\n".join(lines)

    def _default_value(self, type_hint: str) -> str:
        """根据类型提示生成默认测试值"""
        type_map = {
            "int": "1",
            "float": "1.0",
            "str": "'test'",
            "bool": "True",
            "list": "[]",
            "dict": "{}",
            "tuple": "()",
            "set": "set()",
            "bytes": "b''",
        }
        return type_map.get(type_hint, "None")

    def _edge_value(self, type_hint: str) -> str:
        """根据类型提示生成边界测试值"""
        type_map = {
            "int": "0",
            "float": "0.0",
            "str": "''",
            "bool": "False",
            "list": "[]",
            "dict": "{}",
        }
        return type_map.get(type_hint, "None")

    def generate_file(self, source_path: Path, output_path: Path, target_func: str | None = None):
        """为整个文件生成测试"""
        info = self.analyze_file(source_path)
        module_name = source_path.stem

        lines = [
            f'"""自动生成的测试 - {source_path.name}"""',
            "",
            "import pytest",
            f"from {module_name} import *",
            "",
            "",
        ]

        for func in info["functions"]:
            if target_func and func["name"] != target_func:
                continue
            lines.append(self.generate_test(func, module_name))

        for cls in info["classes"]:
            for method in cls["methods"]:
                if target_func and method["name"] != target_func:
                    continue
                lines.append(self.generate_test(method, f"{module_name}.{cls['name']}"))

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="测试生成工具")
    parser.add_argument("--file", help="源文件路径")
    parser.add_argument("--dir", help="源目录路径")
    parser.add_argument("--output", help="测试文件输出路径")
    parser.add_argument("--output-dir", help="批量输出目录")
    parser.add_argument("--function", help="只生成指定函数的测试")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("请指定 --file 或 --dir")

    gen = TestGenerator()

    if args.file:
        source = Path(args.file)
        output = Path(args.output) if args.output else Path(f"tests/test_{source.stem}.py")
        result = gen.generate_file(source, output, args.function)
        print(f"[OK] 测试已生成: {result}")

    if args.dir:
        source_dir = Path(args.dir)
        output_dir = Path(args.output_dir) if args.output_dir else Path("tests")
        for py_file in source_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            output = output_dir / f"test_{py_file.name}"
            result = gen.generate_file(py_file, output, args.function)
            print(f"[OK] 测试已生成: {result}")


if __name__ == "__main__":
    main()
