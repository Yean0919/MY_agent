"""代码审查脚本 - 扫描代码文件并输出问题清单"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


class CodeReviewer:
    """Python 代码审查器"""

    def __init__(self, focus: list[str] | None = None):
        self.focus = focus or ["correctness", "performance", "security", "maintainability", "style"]
        self.issues: list[dict[str, Any]] = []

    def review_file(self, file_path: Path) -> list[dict[str, Any]]:
        """审查单个文件"""
        if not file_path.exists():
            return [{"file": str(file_path), "line": 0, "level": "error", "message": "文件不存在"}]

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return [{"file": str(file_path), "line": e.lineno or 0, "level": "error", "message": f"语法错误: {e.msg}"}]
        except Exception as e:
            return [{"file": str(file_path), "line": 0, "level": "error", "message": f"读取失败: {e}"}]

        issues = []
        lines = content.split("\n")

        if "correctness" in self.focus:
            issues.extend(self._check_correctness(file_path, tree, lines))
        if "performance" in self.focus:
            issues.extend(self._check_performance(file_path, tree, lines))
        if "security" in self.focus:
            issues.extend(self._check_security(file_path, tree, lines))
        if "maintainability" in self.focus:
            issues.extend(self._check_maintainability(file_path, tree, lines))
        if "style" in self.focus:
            issues.extend(self._check_style(file_path, tree, lines))

        return issues

    def _check_correctness(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            # 检查空 except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({
                    "file": str(path), "line": node.lineno, "level": "warning",
                    "dimension": "correctness", "message": "裸 except 会捕获所有异常，建议指定异常类型"
                })
            # 检查可变默认参数
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "file": str(path), "line": node.lineno, "level": "warning",
                            "dimension": "correctness", "message": f"函数 '{node.name}' 使用了可变默认参数，可能导致意外行为"
                        })
        return issues

    def _check_performance(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            # 检查循环内的字符串拼接
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                            issues.append({
                                "file": str(path), "line": child.lineno, "level": "info",
                                "dimension": "performance", "message": "循环内字符串拼接，建议使用 join() 或 io.StringIO"
                            })
        return issues

    def _check_security(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        content = "\n".join(lines)
        # 检查硬编码密钥
        import re
        key_patterns = [
            (r'(?i)(api_key|apikey|secret|password|token)\s*=\s*["\'][^"\']{8,}["\']', "疑似硬编码密钥"),
            (r'(?i)eval\s*\(', "使用 eval() 存在代码注入风险"),
            (r'(?i)exec\s*\(', "使用 exec() 存在代码注入风险"),
            (r'(?i)__import__\s*\(', "动态导入可能被滥用"),
        ]
        for pattern, msg in key_patterns:
            for match in re.finditer(pattern, content):
                lineno = content[:match.start()].count("\n") + 1
                issues.append({
                    "file": str(path), "line": lineno, "level": "warning",
                    "dimension": "security", "message": msg
                })
        return issues

    def _check_maintainability(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 检查函数长度
                end_line = getattr(node, "end_lineno", node.lineno)
                func_lines = end_line - node.lineno
                if func_lines > 50:
                    issues.append({
                        "file": str(path), "line": node.lineno, "level": "info",
                        "dimension": "maintainability", "message": f"函数 '{node.name}' 有 {func_lines} 行，建议拆分为更小的函数"
                    })
                # 检查参数数量
                args = node.args
                total_args = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
                if total_args > 5:
                    issues.append({
                        "file": str(path), "line": node.lineno, "level": "info",
                        "dimension": "maintainability", "message": f"函数 '{node.name}' 有 {total_args} 个参数，建议使用数据类或配置对象"
                    })
        return issues

    def _check_style(self, path: Path, tree: ast.AST, lines: list[str]) -> list[dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 检查是否有 docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                    issues.append({
                        "file": str(path), "line": node.lineno, "level": "info",
                        "dimension": "style", "message": f"函数 '{node.name}' 缺少 docstring"
                    })
        return issues


def format_text(issues: list[dict]) -> str:
    """文本格式输出"""
    if not issues:
        return "[OK] 未发现问题"
    lines = [f"共发现 {len(issues)} 个问题:\n"]
    for i, issue in enumerate(issues, 1):
        level_icon = {"error": "[ERR]", "warning": "[WARN]", "info": "[INFO]"}.get(issue["level"], "•")
        dim = f"[{issue.get('dimension', '?')}]" if "dimension" in issue else ""
        lines.append(f"  {i}. {level_icon} {issue['file']}:{issue['line']} {dim} {issue['message']}")
    return "\n".join(lines)


def format_json(issues: list[dict]) -> str:
    """JSON 格式输出"""
    return json.dumps({"total": len(issues), "issues": issues}, ensure_ascii=False, indent=2)


def format_markdown(issues: list[dict]) -> str:
    """Markdown 格式输出"""
    if not issues:
        return "# 代码审查报告\n\n未发现问题\n"
    lines = [f"# 代码审查报告\n\n共发现 **{len(issues)}** 个问题\n"]
    lines.append("| # | 级别 | 维度 | 文件 | 行 | 问题 |")
    lines.append("|---|------|------|------|-----|------|")
    for i, issue in enumerate(issues, 1):
        level = {"error": "❌ 错误", "warning": "⚠️ 警告", "info": "ℹ️ 提示"}.get(issue["level"], issue["level"])
        dim = issue.get("dimension", "-")
        lines.append(f"| {i} | {level} | {dim} | `{issue['file']}` | {issue['line']} | {issue['message']} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="代码审查工具")
    parser.add_argument("--file", help="审查单个文件")
    parser.add_argument("--dir", help="审查目录")
    parser.add_argument("--focus", default="correctness,performance,security,maintainability,style", help="审查维度")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="输出格式")
    parser.add_argument("--max-issues", type=int, default=20, help="最大问题数")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("请指定 --file 或 --dir")

    reviewer = CodeReviewer(focus=args.focus.split(","))
    all_issues = []

    files = []
    if args.file:
        files.append(Path(args.file))
    if args.dir:
        files.extend(Path(args.dir).rglob("*.py"))

    for f in files:
        all_issues.extend(reviewer.review_file(f))

    all_issues = all_issues[:args.max_issues]

    if args.format == "json":
        print(format_json(all_issues))
    elif args.format == "markdown":
        print(format_markdown(all_issues))
    else:
        print(format_text(all_issues))


if __name__ == "__main__":
    main()
