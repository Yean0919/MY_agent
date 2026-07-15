"""代码专家 Agent"""

import re
from pathlib import Path
from typing import Any

from src.core.agent import BaseAgent
from src.core.llm import call_llm


def _extract_code_block(text: str) -> str:
    """从 LLM 回复中提取代码块内容（去除 markdown 包裹）"""
    # 匹配 ```language ... ``` 或 ``` ... ```
    pattern = r"```(?:\w*)\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # 没有代码块，返回原文
    return text.strip()


def _infer_filename(request: str, language: str) -> str:
    """从任务描述中推断文件名"""
    ext_map = {
        "python": "py",
        "py": "py",
        "javascript": "js",
        "js": "js",
        "typescript": "ts",
        "ts": "ts",
        "html": "html",
        "css": "css",
        "json": "json",
        "yaml": "yaml",
        "yml": "yml",
        "md": "md",
        "markdown": "md",
        "sh": "sh",
        "bash": "sh",
        "c": "c",
        "cpp": "cpp",
        "java": "java",
        "go": "go",
        "rust": "rs",
        "rs": "rs",
    }
    ext = ext_map.get(language.lower(), "txt")

    # 尝试从请求中提取文件名（如 "保存到 xxx.py"、"xxx.py"）
    file_match = re.search(r"[\w\-]+\.(\w+)", request)
    if file_match:
        return file_match.group(0)

    # 尝试提取有意义的单词作为文件名
    word_match = re.search(r"[一-鿿\w]{2,}", request)
    if word_match:
        name = re.sub(r"[^\w]", "", word_match.group(0))[:30]
        if name:
            return f"{name}.{ext}"

    return f"output.{ext}"


class CoderAgent(BaseAgent):
    """代码专家，负责编写和修改代码，并自动保存到文件"""

    def __init__(self) -> None:
        super().__init__(name="coder", description="编写和修改代码")

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行代码编写任务，并自动将生成的代码保存到文件

        Args:
            input_data: 包含 code_request, output_path, language 字段
                - code_request/task: 代码需求描述
                - output_path: 输出文件路径（可选，自动推断）
                - language: 编程语言（默认 python）

        Returns:
            包含 generated_code, output_path, file_size, status 字段
        """
        request = input_data.get("code_request", "") or input_data.get("task", "")
        language = input_data.get("language", "python")
        output_path = input_data.get("output_path", "")

        if not request:
            return {
                "generated_code": "",
                "language": language,
                "status": "error",
                "message": "No code request provided",
            }

        try:
            generated_code = await call_llm(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"请用 {language} 编写代码实现以下需求。"
                            f"只输出代码，用 markdown 代码块包裹，不要额外解释。\n\n"
                            f"需求：{request}"
                        ),
                    }
                ],
                system_prompt="你是一个经验丰富的软件工程师，代码简洁、规范、有注释。",
            )

            # 提取纯代码（去除 markdown 包裹）
            code = _extract_code_block(generated_code)

            # 清理非法 Unicode surrogate 字符
            code = code.encode("utf-8", errors="replace").decode("utf-8")

            # 确定输出路径
            if not output_path:
                output_path = _infer_filename(request, language)

            # 写入文件
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code, encoding="utf-8")

            # 验证文件确实写入成功
            if not path.exists() or path.stat().st_size == 0:
                return {
                    "generated_code": code,
                    "language": language,
                    "output_path": str(path),
                    "status": "error",
                    "message": f"File write verification failed: {path}",
                }

            return {
                "generated_code": code,
                "language": language,
                "output_path": str(path),
                "file_size": path.stat().st_size,
                "status": "completed",
            }
        except RuntimeError as e:
            return {
                "generated_code": "",
                "language": language,
                "status": "error",
                "message": str(e),
            }
