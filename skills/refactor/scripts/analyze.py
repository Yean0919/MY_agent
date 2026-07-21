"""代码重构分析脚本 - 检测代码异味并提供重构建议"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


class CodeSmellDetector:
    """代码异味检测器"""

    def __init__(self, smells: list[str] | None = None):
        self.enabled_smells = smells or [
            "long-method", "long-parameter", "duplication", "deep-nesting",
            "god-class", "magic-number", "dead-code", "complex-condition"
        ]

    def analyze_file(self, file_path: Path) -> list[dict[str, Any]]:
        """分析文件中的代码异味"""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        lines = content.split("\n")

        issues = []

        if "long-method" in self.enabled_smells:
            issues.extend(self._check_long_methods(file_path, tree))
        if "long-parameter" in self.enabled_smells:
            issues.extend(self._check_long_parameters(file_path, tree))
        if "deep-nesting" in self.enabled_smells:
            issues.extend(self._check_deep_nesting(file_path, tree))
        if "god-class" in self.enabled_smells:
            issues.extend(self._check_god_class(file_path, tree))
        if "magic-number" in self.enabled_smells:
            issues.extend(self._check_magic_numbers(file_path, tree, lines))
        if "complex-condition" in self.enabled_smells:
            issues.extend(self._check_complex_conditions(file_path, tree))
        if "dead-code" in self.enabled_smells:
            issues.extend(self._check_dead_code(file_path, tree))

        return issues

    def _check_long_methods(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno)
                length = end_line - node.lineno
                if length > 50:
                    issues.append({
                        "file": str(path), "line": node.lineno,
                        "smell": "long-method", "severity": "medium",
                        "message": f"函数 '{node.name}' 有 {length} 行",
                        "refactor": "提取方法 (Extract Method): 将函数拆分为多个职责单一的小函数"
                    })
        return issues

    def _check_long_parameters(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total = len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
                if total > 5:
                    issues.append({
                        "file": str(path), "line": node.lineno,
                        "smell": "long-parameter", "severity": "medium",
                        "message": f"函数 '{node.name}' 有 {total} 个参数",
                        "refactor": "引入参数对象 (Introduce Parameter Object): 将相关参数封装为数据类"
                    })
        return issues

    def _check_deep_nesting(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                depth = self._get_max_depth(node)
                if depth > 4:
                    issues.append({
                        "file": str(path), "line": node.lineno,
                        "smell": "deep-nesting", "severity": "medium",
                        "message": f"函数 '{node.name}' 最大嵌套深度 {depth} 层",
                        "refactor": "使用卫语句 (Guard Clauses): 提前返回减少嵌套"
                    })
        return issues

    def _get_max_depth(self, node: ast.AST, depth: int = 0) -> int:
        max_depth = depth
        nesting_nodes = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.ExceptHandler)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                max_depth = max(max_depth, self._get_max_depth(child, depth + 1))
            else:
                max_depth = max(max_depth, self._get_max_depth(child, depth))
        return max_depth

    def _check_god_class(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                end_line = getattr(node, "end_lineno", node.lineno)
                length = end_line - node.lineno
                method_count = sum(1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                if length > 300 or method_count > 20:
                    issues.append({
                        "file": str(path), "line": node.lineno,
                        "smell": "god-class", "severity": "high",
                        "message": f"类 '{node.name}' 有 {length} 行、{method_count} 个方法",
                        "refactor": "提取类 (Extract Class): 将不相关的职责拆分到独立的类中"
                    })
        return issues

    def _check_magic_numbers(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in (0, 1, -1, 2, 10, 100):
                    lineno = getattr(node, "lineno", 0)
                    issues.append({
                        "file": str(path), "line": lineno,
                        "smell": "magic-number", "severity": "low",
                        "message": f"魔法数字 {node.value}",
                        "refactor": "提取常量 (Extract Constant): 将魔法数字定义为有意义的常量"
                    })
        return issues

    def _check_complex_conditions(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp) and len(node.values) > 3:
                lineno = getattr(node, "lineno", 0)
                issues.append({
                    "file": str(path), "line": lineno,
                    "smell": "complex-condition", "severity": "medium",
                    "message": f"复杂条件表达式（{len(node.values)} 个条件）",
                    "refactor": "提取方法: 将复杂条件提取为有命名的布尔函数"
                })
        return issues

    def _check_dead_code(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        defined_funcs = set()
        called_funcs = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_") and node.name != "__init__":
                    defined_funcs.add((node.name, node.lineno))
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_funcs.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_funcs.add(node.func.attr)

        for name, lineno in defined_funcs:
            if name not in called_funcs and name not in ("main", "test_", "setUp", "tearDown"):
                issues.append({
                    "file": str(path), "line": lineno,
                    "smell": "dead-code", "severity": "low",
                    "message": f"函数 '{name}' 可能未被使用",
                    "refactor": "如果确认未使用，直接删除"
                })
        return issues


def format_text(issues: list[dict]) -> str:
    if not issues:
        return "[OK] 未发现代码异味"
    lines = [f"共发现 {len(issues)} 个代码异味:\n"]
    for i, issue in enumerate(issues, 1):
        sev_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(issue["severity"], "•")
        lines.append(f"  {i}. {sev_icon} [{issue['smell']}] {issue['file']}:{issue['line']}")
        lines.append(f"     问题: {issue['message']}")
        lines.append(f"     建议: {issue['refactor']}")
        lines.append("")
    return "\n".join(lines)


def format_json(issues: list[dict]) -> str:
    return json.dumps({"total": len(issues), "issues": issues}, ensure_ascii=False, indent=2)


def format_markdown(issues: list[dict]) -> str:
    if not issues:
        return "# 代码重构报告\n\n未发现代码异味\n"
    lines = [f"# 代码重构报告\n\n共发现 **{len(issues)}** 个代码异味\n"]
    lines.append("| # | 严重度 | 类型 | 文件 | 行 | 问题 | 重构建议 |")
    lines.append("|---|--------|------|------|-----|------|----------|")
    for i, issue in enumerate(issues, 1):
        sev = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(issue["severity"], issue["severity"])
        lines.append(f"| {i} | {sev} | {issue['smell']} | `{issue['file']}` | {issue['line']} | {issue['message']} | {issue['refactor']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="代码重构分析工具")
    parser.add_argument("--file", help="分析单个文件")
    parser.add_argument("--dir", help="分析目录")
    parser.add_argument("--smell", help="只检测特定类型的代码异味")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("请指定 --file 或 --dir")

    smells = args.smell.split(",") if args.smell else None
    detector = CodeSmellDetector(smells)
    all_issues = []

    files = []
    if args.file:
        files.append(Path(args.file))
    if args.dir:
        files.extend(Path(args.dir).rglob("*.py"))

    for f in files:
        all_issues.extend(detector.analyze_file(f))

    if args.format == "json":
        print(format_json(all_issues))
    elif args.format == "markdown":
        print(format_markdown(all_issues))
    else:
        print(format_text(all_issues))


if __name__ == "__main__":
    main()
