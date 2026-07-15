"""聊天路由 - 多轮对话 API"""

import time
from typing import Any

from fastapi import APIRouter, Body

from src.agents.tool_using_agent import ToolUsingAgent
from src.core.session_manager import SessionManager
from src.core.task_store import TaskStore
from src.tools.registry import ToolRegistry

router = APIRouter()

# 模块级实例
_session_manager = SessionManager()
_tool_registry = ToolRegistry()
_task_store = TaskStore()


def _get_agent(workspace_path: str = ".") -> ToolUsingAgent:
    """获取工具调用 Agent 实例"""
    return ToolUsingAgent(
        tool_registry=_tool_registry,
        max_tool_iterations=10,
        workspace_path=workspace_path,
    )


@router.post("/")
async def chat(
    message: str = Body(..., embed=True),
    session_id: str = Body("", embed=True),
    workspace_path: str = Body(".", embed=True),
) -> dict[str, Any]:
    """发送聊天消息

    Args:
        message: 用户消息
        session_id: 会话 ID（空则创建新会话）
        workspace_path: 工作目录

    Returns:
        Agent 回复
    """
    # 创建或获取会话
    if not session_id:
        session_id = _session_manager.create_session(title=message[:50])

    # 保存用户消息
    _session_manager.add_message(session_id, "user", message)

    # 获取对话历史（只保留 role 和 content）
    history = _session_manager.get_history(session_id)
    clean_history = [
        {"role": h.get("role", "user"), "content": h.get("content", "")}
        for h in history
        if h.get("content")
    ]

    # 提交任务到任务队列
    task_id = _task_store.submit(message, session_id)
    _task_store.update_status(task_id, "running")

    start_time = time.time()

    try:
        agent = _get_agent(workspace_path)
        result = await agent.chat(message, clean_history)

        duration = time.time() - start_time

        # 保存 Agent 回复
        response_text = result.get("response", "")
        _session_manager.add_message(session_id, "assistant", response_text)

        # 保存工具调用记录（仅记录名称，不保存详细内容到会话历史）
        tool_calls = result.get("tool_calls", [])
        if tool_calls:
            tool_summary = ", ".join(tc.get("name", "") for tc in tool_calls)
            _session_manager.add_message(
                session_id,
                "tool",
                f"Called tools: {tool_summary}",
            )

        # 更新任务状态
        _task_store.update_result(task_id, result, duration)
        _task_store.update_status(task_id, "success")

        # 自动更新会话标题（用第一条用户消息）
        msg_count = _session_manager.get_message_count(session_id)
        if msg_count <= 2:
            _session_manager.update_session_title(session_id, message[:50])

        return {
            "session_id": session_id,
            "task_id": task_id,
            "response": response_text,
            "tool_calls": tool_calls,
            "metadata": {"duration": round(duration, 2)},
        }

    except Exception as e:
        duration = time.time() - start_time
        _task_store.update_error(task_id, str(e))
        return {
            "session_id": session_id,
            "task_id": task_id,
            "response": "",
            "error": str(e),
            "metadata": {"duration": round(duration, 2)},
        }


@router.get("/sessions")
async def list_sessions(limit: int = 50) -> dict[str, Any]:
    """列出所有会话

    Args:
        limit: 最多返回数

    Returns:
        会话列表
    """
    sessions = _session_manager.list_sessions(limit=limit)
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 100) -> dict[str, Any]:
    """获取会话历史

    Args:
        session_id: 会话 ID
        limit: 最多返回消息数

    Returns:
        消息历史
    """
    session = _session_manager.get_session(session_id)
    if not session:
        return {"error": f"Session not found: {session_id}"}

    messages = _session_manager.get_history(session_id, limit=limit)
    return {
        "session": session,
        "messages": messages,
        "count": len(messages),
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict[str, Any]:
    """删除会话

    Args:
        session_id: 会话 ID

    Returns:
        删除结果
    """
    deleted = _session_manager.delete_session(session_id)
    if deleted:
        return {"status": "deleted", "session_id": session_id}
    return {"error": f"Session not found: {session_id}"}


@router.post("/session/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
) -> dict[str, Any]:
    """更新会话标题

    Args:
        session_id: 会话 ID
        title: 新标题

    Returns:
        更新结果
    """
    session = _session_manager.get_session(session_id)
    if not session:
        return {"error": f"Session not found: {session_id}"}

    _session_manager.update_session_title(session_id, title)
    return {"status": "updated", "session_id": session_id, "title": title}
