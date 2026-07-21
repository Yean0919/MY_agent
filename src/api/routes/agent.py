"""Agent 路由"""

import time
from typing import Any

from fastapi import APIRouter

from src.agents.orchestrator import Orchestrator
from src.agents.roles.coder import CoderAgent
from src.agents.roles.researcher import ResearcherAgent
from src.agents.roles.reviewer import ReviewerAgent
from src.agents.roles.tester import TesterAgent
from src.api.schemas.requests import AgentRequest
from src.core.task_store import TaskStore
from src.core.token_tracker import get_token_stats

router = APIRouter()

# 模块级任务存储（API 和面板共享）
_task_store = TaskStore()


def _build_orchestrator() -> Orchestrator:
    """构建带角色 Agent 的编排器"""
    orchestrator = Orchestrator()
    orchestrator.register_agent(ResearcherAgent())
    orchestrator.register_agent(CoderAgent())
    orchestrator.register_agent(ReviewerAgent())
    orchestrator.register_agent(TesterAgent())
    return orchestrator


@router.post("/run")
async def run_agent(request: AgentRequest) -> dict[str, Any]:
    """运行 Agent

    Args:
        request: Agent 请求

    Returns:
        Agent 执行结果
    """
    session_id = request.session_id or "default"

    # 提交任务到任务队列
    task_id = _task_store.submit(request.task, session_id)
    _task_store.update_status(task_id, "running")

    start_time = time.time()

    try:
        orchestrator = _build_orchestrator()
        result = await orchestrator.execute({"task": request.task, "context": request.context})

        duration = time.time() - start_time

        # 保存结果
        _task_store.update_plan(task_id, result.get("plan", []))
        _task_store.update_result(task_id, result, duration)

        # 检查是否有 Agent 执行失败
        agent_results = result.get("results", [])
        has_error = any(item.get("status") == "error" for item in agent_results)
        if has_error:
            errors = [
                f"{item.get('agent')}: {item.get('message', 'unknown')}"
                for item in agent_results
                if item.get("status") == "error"
            ]
            _task_store.update_error(task_id, "; ".join(errors))
        else:
            _task_store.update_status(task_id, "success")

        return {
            "task_id": task_id,
            "result": result,
            "session_id": session_id,
            "metadata": {"duration": round(duration, 2)},
        }

    except Exception as e:
        duration = time.time() - start_time
        _task_store.update_error(task_id, str(e))
        return {
            "task_id": task_id,
            "result": None,
            "session_id": session_id,
            "error": str(e),
            "metadata": {"duration": round(duration, 2)},
        }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """获取任务状态

    Args:
        task_id: 任务 ID

    Returns:
        任务状态信息
    """
    task = _task_store.get_by_id(task_id)
    if not task:
        return {"error": f"Task not found: {task_id}"}
    return task


@router.get("/list")
async def list_tasks(
    session_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """列出任务

    Args:
        session_id: 按会话过滤
        status: 按状态过滤
        limit: 最多返回数

    Returns:
        任务列表
    """
    tasks = _task_store.list_tasks(session_id=session_id, status=status, limit=limit)
    return {"tasks": tasks, "count": len(tasks)}


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    """获取任务统计

    Returns:
        统计信息
    """
    return {
        "total": _task_store.get_total_count(),
        "success": _task_store.get_success_count(),
        "error": _task_store.get_error_count(),
        "by_status": _task_store.get_stats(),
    }


@router.get("/token-usage")
async def get_token_usage() -> dict[str, Any]:
    """获取 Token 消耗统计

    Returns:
        Token 使用量统计（总量、按 Agent 分组、按模型分组）
    """
    return get_token_stats().summary()
