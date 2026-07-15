"""工具调用 Agent - 支持多轮对话和工具调用"""

import json
import re
from pathlib import Path
from typing import Any, cast

from src.core.agent import BaseAgent
from src.core.llm import call_llm
from src.tools.registry import ToolRegistry


def _verify_file_write(
    tool_name: str, arguments: dict[str, Any], tool_result: dict[str, Any]
) -> str | None:
    """验证 write 工具调用后文件是否真的写入成功

    Returns:
        错误信息字符串，或 None 表示验证通过
    """
    if tool_name != "write":
        return None
    if not tool_result.get("success"):
        return None  # 工具自己已经报错了，不需要重复验证

    file_path = arguments.get("file_path", "")
    if not file_path:
        return None

    path = Path(file_path)
    if not path.exists():
        return f"Write verification failed: file does not exist at {file_path}"
    if path.stat().st_size == 0:
        return f"Write verification failed: file is empty at {file_path}"
    return None


class ToolUsingAgent(BaseAgent):
    """工具调用 Agent，支持对话式交互和工具调用"""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        max_tool_iterations: int = 10,
        workspace_path: str = ".",
    ) -> None:
        super().__init__(name="assistant", description="对话式 AI 助手，可以调用工具")
        self.tool_registry = tool_registry
        self.max_tool_iterations = max_tool_iterations
        self.workspace_path = workspace_path

    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        tools = self.tool_registry.list_tools()
        tools_json = json.dumps(tools, ensure_ascii=False, indent=2)

        return f"""你是一个智能编程助手。你可以与用户对话，并调用工具来完成任务。

## 可用工具
{tools_json}

## 工具调用格式
当你需要调用工具时，在回复中包含以下 JSON 格式的工具调用：
```tool_call
{{
    "name": "工具名称",
    "arguments": {{
        "参数名": "参数值"
    }}
}}
```

## 规则
1. 如果可以直接回答用户的问题，直接回复，不要调用工具
2. 如果需要读取/修改文件、执行命令等，调用相应的工具
3. 每次只调用一个工具
4. 调用工具后，根据工具返回的结果继续对话
5. 代码用 markdown 代码块包裹
6. 保持回复简洁、有用
7. 工作目录: {self.workspace_path}
"""

    def _parse_tool_call(self, response: str) -> dict[str, Any] | None:
        """从 LLM 回复中解析工具调用

        Args:
            response: LLM 回复文本

        Returns:
            工具调用字典或 None
        """
        # 查找 ```tool_call 代码块
        pattern = r"```tool_call\s*\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                return cast(dict[str, Any], json.loads(match.group(1)))
            except json.JSONDecodeError:
                pass

        # 查找行内 JSON 工具调用
        pattern = r'\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}'
        match = re.search(pattern, response)
        if match:
            try:
                return cast(dict[str, Any], json.loads(match.group(0)))
            except json.JSONDecodeError:
                pass

        return None

    def _extract_text_response(self, response: str) -> str:
        """从 LLM 回复中提取纯文本（去除工具调用部分）"""
        # 移除 tool_call 代码块
        text = re.sub(r"```tool_call\s*\n.*?\n```", "", response, flags=re.DOTALL)
        return text.strip()

    async def chat(
        self,
        message: str,
        history: list[dict[str, Any]],
        *,
        workspace_path: str | None = None,
    ) -> dict[str, Any]:
        """处理一条对话消息

        Args:
            message: 用户消息
            history: 对话历史
            workspace_path: 工作目录

        Returns:
            包含 response, tool_calls, final 的字典
        """
        # 构建消息列表
        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史消息
        for h in history[-20:]:  # 限制历史长度
            role = h.get("role", "user")
            content = h.get("content", "")
            if content and role in ("user", "assistant", "tool"):
                msg = {"role": role, "content": content}
                if role == "tool":
                    msg["tool_call_id"] = h.get("tool_call_id", "call_0")
                messages.append(msg)

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        tool_calls_made: list[dict[str, Any]] = []
        final_response = ""

        # 工具调用循环
        for _ in range(self.max_tool_iterations):
            try:
                response = await call_llm(messages=messages)
            except RuntimeError as e:
                return {
                    "response": f"Error calling LLM: {e}",
                    "tool_calls": tool_calls_made,
                    "final": True,
                    "error": str(e),
                }

            # 检查是否有工具调用
            tool_call = self._parse_tool_call(response)

            if tool_call:
                tool_name = tool_call.get("name", "")
                arguments = tool_call.get("arguments", {})

                # 记录工具调用
                tool_calls_made.append({"name": tool_name, "arguments": arguments})

                # 调用工具
                tool_result = await self.tool_registry.call_tool(tool_name, arguments)

                # 写文件后验证：确保文件真的写入磁盘
                verify_error = _verify_file_write(tool_name, arguments, tool_result)
                if verify_error:
                    tool_result = {"success": False, "error": verify_error}

                # 构建工具结果消息
                if tool_result.get("success"):
                    result_text = json.dumps(tool_result.get("result", ""), ensure_ascii=False)
                else:
                    result_text = f"Error: {tool_result.get('error', 'Unknown error')}"

                # 添加工具结果到消息历史
                tool_call_id = f"call_{len(tool_calls_made)}"
                messages.append({"role": "assistant", "content": response})
                messages.append(
                    {"role": "tool", "content": result_text, "tool_call_id": tool_call_id}
                )

                continue

            # 没有工具调用，这是最终回复
            final_response = self._extract_text_response(response)
            break

        return {
            "response": final_response,
            "tool_calls": tool_calls_made,
            "final": True,
        }

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行 Agent（兼容 BaseAgent 接口）

        Args:
            input_data: 输入数据，包含 message 和 history

        Returns:
            执行结果
        """
        message = input_data.get("message", "") or input_data.get("task", "")
        history = input_data.get("history", [])
        workspace_path = input_data.get("workspace_path")

        if not message:
            return {
                "response": "Please provide a message.",
                "tool_calls": [],
                "final": True,
            }

        return await self.chat(message, history, workspace_path=workspace_path)
