"""Bug 排查脚本 - 检测 Python 代码中的常见 Bug 模式"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


class BugHunter:
    """Bug 检测器"""

    def __init__(self, bug_types: list[str] | None = None, min_severity: str = "medium"):
        self.enabled_types = bug_types or [
            "null-access", "resource-leak", "type-mismatch", "exception-swallow",
            "index-out-of-range", "import-error", "unused-variable", "mutable-default"
        ]
        self.severity_order = {"low": 0, "medium": 1, "high": 2}
        self.min_severity = self.severity_order.get(min_severity, 1)

    def analyze_file(self, file_path: Path) -> list[dict[str, Any]]:
        """分析文件中的 Bug"""
        content = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return [{"file": str(file_path), "line": e.lineno or 0, "severity": "high",
                     "bug": "syntax-error", "message": f"语法错误: {e.msg}", "fix": "修复语法错误"}]

        issues = []

        if "null-access" in self.enabled_types:
            issues.extend(self._check_null_access(file_path, tree))
        if "resource-leak" in self.enabled_types:
            issues.extend(self._check_resource_leak(file_path, tree))
        if "exception-swallow" in self.enabled_types:
            issues.extend(self._check_exception_swallow(file_path, tree))
        if "mutable-default" in self.enabled_types:
            issues.extend(self._check_mutable_default(file_path, tree))
        if "unused-variable" in self.enabled_types:
            issues.extend(self._check_unused_variable(file_path, tree))
        if "index-out-of-range" in self.enabled_types:
            issues.extend(self._check_index_access(file_path, tree))
        if "type-mismatch" in self.enabled_types:
            issues.extend(self._check_type_mismatch(file_path, tree))

        # 过滤严重度
        issues = [i for i in issues if self.severity_order.get(i["severity"], 0) >= self.min_severity]
        return issues

    def _check_null_access(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            # 检查链式调用: obj.method() 而没有检查 obj 是否为 None
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    # 简单启发式: 如果变量名包含 none, null, nil
                    name = node.func.value.id.lower()
                    if any(x in name for x in ["none", "null", "nil"]):
                        issues.append({
                            "file": str(path), "line": node.lineno, "severity": "high",
                            "bug": "null-access", "message": f"可能的空值访问: '{node.func.value.id}'",
                            "fix": "在访问前检查是否为 None"
                        })
        return issues

    def _check_resource_leak(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            # 检查 open() 调用不在 with 语句中
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "open":
                    # 检查父节点是否是 with 语句
                    # 简单启发式: 如果 open() 的结果被赋值给变量而不是 with
                    parent = getattr(node, "_parent", None)
                    if isinstance(parent, ast.Assign):
                        issues.append({
                            "file": str(path), "line": node.lineno, "severity": "high",
                            "bug": "resource-leak", "message": "open() 未使用 with 语句",
                            "fix": "使用 with open(...) as f: 确保文件正确关闭"
                        })
        return issues

    def _check_exception_swallow(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # 检查空 except 块
                if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
                    issues.append({
                        "file": str(path), "line": node.lineno, "severity": "high",
                        "bug": "exception-swallow", "message": "异常被静默吞没",
                        "fix": "至少记录日志: logging.exception('error occurred')"
                    })
                # 检查裸 except
                if node.type is None:
                    issues.append({
                        "file": str(path), "line": node.lineno, "severity": "medium",
                        "bug": "exception-swallow", "message": "裸 except 会捕获所有异常",
                        "fix": "指定具体异常类型: except ValueError as e:"
                    })
        return issues

    def _check_mutable_default(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "file": str(path), "line": node.lineno, "severity": "medium",
                            "bug": "mutable-default", "message": f"函数 '{node.name}' 使用可变默认参数",
                            "fix": "使用 None 作为默认值，在函数内检查并初始化"
                        })
        return issues

    def _check_unused_variable(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        assigned = set()
        used = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned.add((target.id, target.lineno))
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used.add(node.id)

        for name, lineno in assigned:
            if name.startswith("_"):
                continue
            if name not in used and not name.startswith("test_"):
                issues.append({
                    "file": str(path), "line": lineno, "severity": "low",
                    "bug": "unused-variable", "message": f"变量 '{name}' 赋值后未使用",
                    "fix": "删除未使用的变量，或用 _ 前缀表示有意忽略"
                })
        return issues

    def _check_index_access(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                # 检查硬编码索引
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
                    if node.slice.value > 5:
                        issues.append({
                            "file": str(path), "line": node.lineno, "severity": "low",
                            "bug": "index-out-of-range", "message": f"硬编码索引 [{node.slice.value}]，可能越界",
                            "fix": "先检查长度: if len(lst) > index: ..."
                        })
        return issues

    def _check_type_mismatch(self, path: Path, tree: ast.AST) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            # 检查字符串 + 数字
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
                left_str = isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)
                right_str = isinstance(node.right, ast.Constant) and isinstance(node.right.value, str)
                if left_str != right_str and (left_str or right_str):
                    issues.append({
                        "file": str(path), "line": node.lineno, "severity": "medium",
                        "bug": "type-mismatch", "message": "字符串和非字符串相加",
                        "fix": "使用 f-string 或 str() 进行显式转换"
                    })
        return issues


def format_text(issues: list[dict]) -> str:
    if not issues:
        return "[OK] 未发现 Bug"
    lines = [f"共发现 {len(issues)} 个潜在 Bug:\n"]
    for i, issue in enumerate(issues, 1):
        sev_icon = {"high": "[HIGH]", "medium": "[MED]", "low": "[LOW]"}.get(issue["severity"], "•")
        lines.append(f"  {i}. {sev_icon} [{issue['bug']}] {issue['file']}:{issue['line']}")
        lines.append(f"     问题: {issue['message']}")
        lines.append(f"     修复: {issue['fix']}")
        lines.append("")
    return "\n".join(lines)


def format_json(issues: list[dict]) -> str:
    return json.dumps({"total": len(issues), "issues": issues}, ensure_ascii=False, indent=2)


def format_markdown(issues: list[dict]) -> str:
    if not issues:
        return "# Bug 排查报告\n\n未发现 Bug\n"
    lines = [f"# Bug 排查报告\n\n共发现 **{len(issues)}** 个潜在 Bug\n"]
    lines.append("| # | 严重度 | 类型 | 文件 | 行 | 问题 | 修复建议 |")
    lines.append("|---|--------|------|------|-----|------|----------|")
    for i, issue in enumerate(issues, 1):
        sev = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(issue["severity"], issue["severity"])
        lines.append(f"| {i} | {sev} | {issue['bug']} | `{issue['file']}` | {issue['line']} | {issue['message']} | {issue['fix']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Bug 排查工具")
    parser.add_argument("--file", help="扫描单个文件")
    parser.add_argument("--dir", help="扫描目录")
    parser.add_argument("--type", help="只检测特定类型的 Bug")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--severity", choices=["low", "medium", "high"], default="medium")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("请指定 --file 或 --dir")

    bug_types = args.type.split(",") if args.type else None
    hunter = BugHunter(bug_types, args.severity)
    all_issues = []

    files = []
    if args.file:
        files.append(Path(args.file))
    if args.dir:
        files.extend(Path(args.dir).rglob("*.py"))

    for f in files:
        all_issues.extend(hunter.analyze_file(f))

    if args.format == "json":
        print(format_json(all_issues))
    elif args.format == "markdown":
        print(format_markdown(all_issues))
    else:
        print(format_text(all_issues))


if __name__ == "__main__":
    main()
