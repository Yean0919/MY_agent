"""API 文档生成脚本 - 扫描 FastAPI/Flask 路由并生成文档"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any


class APIDocGenerator:
    """API 文档生成器"""

    def analyze_file(self, file_path: Path) -> list[dict[str, Any]]:
        """分析路由文件，提取 API 信息"""
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        apis = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                api_info = self._extract_route_info(node, content)
                if api_info:
                    api_info["file"] = str(file_path)
                    apis.append(api_info)

        return apis

    def _extract_route_info(self, node: ast.FunctionDef, content: str) -> dict | None:
        """从装饰器提取路由信息"""
        for decorator in node.decorator_list:
            route = self._parse_route_decorator(decorator)
            if route:
                return {
                    "method": route["method"],
                    "path": route["path"],
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "parameters": self._extract_params(node),
                    "tags": route.get("tags", []),
                }
        return None

    def _parse_route_decorator(self, dec: ast.expr) -> dict | None:
        """解析路由装饰器"""
        if isinstance(dec, ast.Call):
            func = dec.func
            # @router.get("/path") 或 @app.post("/path")
            if isinstance(func, ast.Attribute):
                method = func.attr.upper()
                if method in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                    if dec.args and isinstance(dec.args[0], ast.Constant):
                        path = dec.args[0].value
                        tags = []
                        for kw in dec.keywords:
                            if kw.arg == "tags" and isinstance(kw.value, ast.List):
                                tags = [e.value for e in kw.value.elts if isinstance(e, ast.Constant)]
                        return {"method": method, "path": path, "tags": tags}
        return None

    def _extract_params(self, node: ast.FunctionDef) -> list[dict]:
        """提取函数参数信息"""
        params = []
        for arg in node.args.args:
            if arg.arg in ("self", "cls", "request", "response", "db", "session"):
                continue
            param = {"name": arg.arg, "type": "", "default": ""}
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            params.append(param)

        # 提取默认值
        defaults = node.args.defaults
        offset = len(node.args.args) - len(defaults)
        for i, default in enumerate(defaults):
            idx = offset + i
            if idx < len(params):
                params[idx]["default"] = ast.unparse(default)

        return params

    def generate_text(self, apis: list[dict]) -> str:
        """生成文本格式文档"""
        if not apis:
            return "未发现 API 路由"

        lines = [f"共发现 {len(apis)} 个 API 接口:\n"]
        for api in apis:
            method_icon = {"GET": "[GET]", "POST": "[POST]", "PUT": "[PUT]", "DELETE": "[DEL]", "PATCH": "[PATCH]"}.get(api["method"], "[?]")
            lines.append(f"  {method_icon} {api['method']:6s} {api['path']}")
            lines.append(f"     函数: {api['name']}")
            if api["docstring"]:
                lines.append(f"     描述: {api['docstring'].split(chr(10))[0]}")
            if api["parameters"]:
                lines.append(f"     参数: {', '.join(p['name'] for p in api['parameters'])}")
            if api["tags"]:
                lines.append(f"     标签: {', '.join(api['tags'])}")
            lines.append("")
        return "\n".join(lines)

    def generate_markdown(self, apis: list[dict]) -> str:
        """生成 Markdown 格式文档"""
        if not apis:
            return "# API Documentation\n\nNo APIs found\n"

        lines = ["# API 文档\n"]
        lines.append(f"共 **{len(apis)}** 个接口\n")

        # 按标签分组
        tagged: dict[str, list] = {}
        for api in apis:
            tag = api["tags"][0] if api["tags"] else "未分类"
            tagged.setdefault(tag, []).append(api)

        for tag, tag_apis in tagged.items():
            lines.append(f"\n## {tag}\n")
            lines.append("| 方法 | 路径 | 函数 | 描述 |")
            lines.append("|------|------|------|------|")
            for api in tag_apis:
                desc = api["docstring"].split("\n")[0] if api["docstring"] else "-"
                lines.append(f"| `{api['method']}` | `{api['path']}` | `{api['name']}` | {desc} |")

            # 详细信息
            for api in tag_apis:
                lines.append(f"\n### `{api['method']}` {api['path']}\n")
                if api["docstring"]:
                    lines.append(f"{api['docstring']}\n")
                if api["parameters"]:
                    lines.append("**参数:**\n")
                    lines.append("| 名称 | 类型 | 默认值 |")
                    lines.append("|------|------|--------|")
                    for p in api["parameters"]:
                        lines.append(f"| `{p['name']}` | `{p['type']}` | `{p['default']}` |")
                    lines.append("")

        return "\n".join(lines)

    def generate_openapi(self, apis: list[dict], title: str = "API") -> str:
        """生成 OpenAPI YAML 格式"""
        paths = {}
        for api in apis:
            path = api["path"]
            method = api["method"].lower()
            if path not in paths:
                paths[path] = {}

            parameters = []
            for p in api["parameters"]:
                param = {"name": p["name"], "in": "query", "schema": {"type": "string"}}
                parameters.append(param)

            paths[path][method] = {
                "summary": api["docstring"].split("\n")[0] if api["docstring"] else api["name"],
                "operationId": api["name"],
                "parameters": parameters,
                "responses": {"200": {"description": "成功"}},
            }
            if api["tags"]:
                paths[path][method]["tags"] = api["tags"]

        spec = {
            "openapi": "3.0.0",
            "info": {"title": title, "version": "1.0.0"},
            "paths": paths,
        }

        return json.dumps(spec, ensure_ascii=False, indent=2)

    def generate_json(self, apis: list[dict]) -> str:
        return json.dumps({"total": len(apis), "apis": apis}, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="API 文档生成工具")
    parser.add_argument("--file", help="路由文件路径")
    parser.add_argument("--dir", help="路由目录路径")
    parser.add_argument("--format", choices=["text", "json", "markdown", "openapi"], default="text")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--title", default="API", help="文档标题")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("请指定 --file 或 --dir")

    gen = APIDocGenerator()
    all_apis = []

    files = []
    if args.file:
        files.append(Path(args.file))
    if args.dir:
        files.extend(Path(args.dir).rglob("*.py"))

    for f in files:
        all_apis.extend(gen.analyze_file(f))

    if args.format == "json":
        output = gen.generate_json(all_apis)
    elif args.format == "markdown":
        output = gen.generate_markdown(all_apis)
    elif args.format == "openapi":
        output = gen.generate_openapi(all_apis, args.title)
    else:
        output = gen.generate_text(all_apis)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 文档已生成: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
