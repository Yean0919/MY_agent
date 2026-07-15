"""Harness Engineering 核心执行引擎 — 使用 langchain 原生工具调用。

所有终端输入统一走 TAOR 循环（Think-Act-Observe-Reflect），
由 LLM 自己决定是直接回复还是调用工具。
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.config.settings import get_settings
from src.core.llm import _get_llm
from src.harness.memory import MemoryItem, MemoryTier, PersistentMemoryStore
from src.harness.tools import TOOLS, get_tools_list

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 异常
# ═══════════════════════════════════════════════════════════


class SafetyViolation(Exception):
    pass


class DeadLoopDetected(Exception):
    pass


class TurnTimeout(Exception):
    pass


# ═══════════════════════════════════════════════════════════
# 状态
# ═══════════════════════════════════════════════════════════


@dataclass
class SafetyPolicy:
    max_tool_calls_per_turn: int = 10
    max_turns_per_session: int = 50
    max_consecutive_same_tool: int = 3
    max_consecutive_errors: int = 5
    timeout_seconds: float = 120.0


@dataclass
class TurnState:
    turn_id: str
    session_id: str
    start_time: float = field(default_factory=time.time)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    consecutive_same_tool: dict[str, int] = field(default_factory=dict)
    consecutive_errors: int = 0
    tool_call_history: list[tuple[str, str]] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# 系统提示词
# ═══════════════════════════════════════════════════════════


def build_system_prompt(project_root: str, memory_context: str = "") -> str:
    """构建系统提示词。"""
    tool_descs = "\n".join(
        f"- {name}: {desc}"
        for name, desc in [
            ("read_file", "读取文件内容"),
            ("write_file", "写入文件（一次性写入完整内容）"),
            ("edit_file", "替换文件中的文本"),
            ("list_dir", "列出目录内容"),
            ("grep", "搜索正则模式"),
            ("find_files", "查找匹配的文件"),
        ]
    )

    memory_section = ""
    if memory_context:
        memory_section = f"\n--- 长期记忆 ---\n{memory_context}\n--- 记忆结束 ---\n"

    return (
        "你是 YEAN，一个专业的编程助手。\n\n"
        "=== 你的角色 ===\n"
        "你可以帮助用户编写代码、调试、重构、文件操作、项目分析、回答技术问题等。\n"
        "对于简单的问答（如自我介绍、概念解释），直接回复即可，不需要调用工具。\n\n"
        "=== 工具使用规则（严格遵守）===\n"
        "1. 写文件时，必须一次性写入完整代码\n"
        "2. 写完文件后，不要再次写同一个文件\n"
        "3. 如果工具执行成功，不要再执行同样的工具\n"
        "4. 每次最多调用 3 个工具\n"
        "5. 完成工作后，直接回复总结\n\n"
        "=== 可用工具 ===\n"
        f"{tool_descs}\n\n"
        f"=== 项目信息 ===\n"
        f"项目目录：{project_root}\n"
        f"{memory_section}"
        "=== 工作原则 ===\n"
        "1. 先理解问题，再行动\n"
        "2. 涉及代码时，先搜索相关代码\n"
        "3. 修改代码前，先读取当前内容\n"
        "4. 完成后，简要总结做了什么"
    )


# ═══════════════════════════════════════════════════════════
# 安全校验器
# ═══════════════════════════════════════════════════════════


class SafetyChecker:
    def __init__(self, policy: SafetyPolicy | None = None):
        self.policy = policy or SafetyPolicy()

    def check_turn_state(self, state: TurnState) -> None:
        elapsed = time.time() - state.start_time
        if elapsed > self.policy.timeout_seconds:
            raise TurnTimeout(f"Turn 超时 ({elapsed:.1f}s)")
        if len(state.tool_calls) >= self.policy.max_tool_calls_per_turn:
            raise SafetyViolation("工具调用次数超限")
        if state.consecutive_errors >= self.policy.max_consecutive_errors:
            raise SafetyViolation("连续错误次数超限")

    def check_dead_loop(self, tool_name: str, tool_args: dict, state: TurnState) -> None:
        call_key = (tool_name, json.dumps(tool_args, sort_keys=True))
        if call_key in state.tool_call_history:
            raise DeadLoopDetected(f"检测到重复工具调用: {tool_name}")

        if "path" in tool_args:
            for t, args_json in state.tool_call_history:
                if t == tool_name:
                    try:
                        args = json.loads(args_json)
                        if args.get("path") == tool_args["path"]:
                            raise DeadLoopDetected(
                                f"检测到重复文件操作: {tool_name} {tool_args['path']}"
                            )
                    except json.JSONDecodeError:
                        pass

        state.tool_call_history.append(call_key)
        state.consecutive_same_tool[tool_name] = state.consecutive_same_tool.get(tool_name, 0) + 1
        for other in list(state.consecutive_same_tool.keys()):
            if other != tool_name:
                state.consecutive_same_tool[other] = 0


# ═══════════════════════════════════════════════════════════
# TAOR 循环
# ═══════════════════════════════════════════════════════════


class AgentLoop:
    """TAOR 循环 — 使用 langchain 原生工具调用。"""

    def __init__(
        self,
        project_root: str,
        memory_store: PersistentMemoryStore,
        safety_checker: SafetyChecker | None = None,
    ):
        self.project_root = project_root
        self.memory_store = memory_store
        self.safety = safety_checker or SafetyChecker()
        self.tools = get_tools_list()

    async def run(
        self,
        user_message: str,
        session_id: str,
        history: list[dict[str, str]],
        max_turns: int = 10,
    ) -> tuple[str, list[dict[str, Any]], TurnState]:
        """执行 TAOR 循环。"""
        turn_id = hashlib.md5(f"{session_id}-{time.time()}".encode()).hexdigest()[:12]
        state = TurnState(turn_id=turn_id, session_id=session_id)
        all_tool_results: list[dict[str, Any]] = []

        # 构建消息
        messages = self._build_messages(user_message, history)

        # 获取 LLM 并绑定工具
        llm = _get_llm()
        llm_with_tools = llm.bind_tools(self.tools)

        for turn in range(max_turns):
            self.safety.check_turn_state(state)

            # Think: 调用 LLM
            logger.info("Turn %d: Thinking...", turn + 1)
            response = await self._think(llm_with_tools, messages, state)

            # 检查是否有工具调用
            if not hasattr(response, "tool_calls") or not response.tool_calls:
                reply = response.content if hasattr(response, "content") else str(response)
                return reply, all_tool_results, state

            # Act: 执行工具
            for tool_call in response.tool_calls[:3]:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})

                self.safety.check_dead_loop(tool_name, tool_args, state)

                logger.info("Turn %d: Acting - %s %s", turn + 1, tool_name, tool_args)

                result = await self._act(tool_name, tool_args, state)

                success = not result.startswith("Error") and not result.startswith("工具执行失败")
                tool_result = {
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result,
                    "success": success,
                }
                all_tool_results.append(tool_result)
                state.tool_calls.append(tool_result)

                if not success:
                    state.consecutive_errors += 1
                else:
                    state.consecutive_errors = 0

                messages.append(response)
                messages.append(
                    ToolMessage(
                        content=result,
                        tool_call_id=tool_call.get("id", f"call_{len(messages)}"),
                    )
                )

        # 最终回复
        final_response = await self._think(llm_with_tools, messages, state)
        return (
            final_response.content if hasattr(final_response, "content") else str(final_response),
            all_tool_results,
            state,
        )

    def _build_messages(
        self,
        user_message: str,
        history: list[dict[str, str]],
    ) -> list[Any]:
        """构建消息列表。"""
        memory_context = ""
        try:
            memories = self.memory_store.retrieve(query=user_message, limit=5)
            if memories:
                memory_context = "\n".join(m.content for m in memories)
        except Exception as e:
            logger.warning("记忆检索失败: %s", e)

        system_prompt = build_system_prompt(self.project_root, memory_context=memory_context)
        messages = [SystemMessage(content=system_prompt)]

        for h in history[-10:]:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))

        messages.append(HumanMessage(content=user_message))
        return messages

    async def _think(self, llm: Any, messages: list[Any], state: TurnState) -> Any:
        """Think: 调用 LLM。"""
        try:
            if hasattr(llm, "ainvoke"):
                response = await llm.ainvoke(messages)
            else:
                response = await llm.chat(messages)
            return response
        except Exception as e:
            state.errors.append(f"LLM 调用失败: {e}")
            raise

    async def _act(self, tool_name: str, tool_args: dict, state: TurnState) -> str:
        """Act: 执行工具。"""
        try:
            tool = TOOLS.get(tool_name)
            if tool is None:
                return f"未知工具: {tool_name}"

            tool_args["base"] = self.project_root

            result = tool.invoke(tool_args)
            return str(result)
        except Exception as e:
            error_msg = f"工具执行失败 [{tool_name}]: {e}"
            state.errors.append(error_msg)
            return error_msg


# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════


async def run_agent(
    user_message: str,
    session_id: str,
    project_root: str,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """运行 Agent。"""
    memory_store = PersistentMemoryStore(db_path=Path(project_root) / "data" / "memory.db")
    safety_checker = SafetyChecker()

    loop = AgentLoop(
        project_root=project_root,
        memory_store=memory_store,
        safety_checker=safety_checker,
    )

    try:
        reply, tool_results, state = await loop.run(user_message, session_id, history or [])
        metadata = {
            "turn_id": state.turn_id,
            "tool_calls": len(state.tool_calls),
            "errors": len(state.errors),
            "duration": time.time() - state.start_time,
        }
        return reply, tool_results, metadata
    except DeadLoopDetected as e:
        logger.warning("死循环检测: %s", e)
        return f"[系统] 检测到可能的死循环，已停止执行: {e}", [], {"error": "dead_loop"}
    except SafetyViolation as e:
        logger.warning("安全违规: %s", e)
        return f"[系统] 安全限制: {e}", [], {"error": "safety_violation"}
    except TurnTimeout as e:
        logger.warning("Turn 超时: %s", e)
        return f"[系统] 执行超时: {e}", [], {"error": "timeout"}
