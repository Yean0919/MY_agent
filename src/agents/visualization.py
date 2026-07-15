"""Streamlit 可视化面板 - 聊天 + 任务提交 + 实时状态 + 执行历史 + 真实指标"""

import json
from typing import Any, cast

import httpx
import streamlit as st

from src.core.session_manager import SessionManager
from src.core.task_store import TaskStore

# API 服务地址
API_BASE_URL = "http://localhost:8000"

# 数据存储
_task_store = TaskStore()
_session_manager = SessionManager()

# Agent 名称列表
AGENTS = ["Orchestrator", "Coder", "Reviewer", "Tester", "Researcher"]

# 页面状态
if "current_session" not in st.session_state:
    st.session_state.current_session = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """API GET 请求"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE_URL}{path}", params=params)
            if response.status_code == 200:
                return cast(dict[str, Any], response.json())
    except Exception:
        pass
    return None


def _api_post(path: str, json_data: dict[str, Any]) -> dict[str, Any] | None:
    """API POST 请求"""
    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(f"{API_BASE_URL}{path}", json=json_data)
            if response.status_code == 200:
                return cast(dict[str, Any], response.json())
    except Exception:
        pass
    return None


def _render_chat() -> None:
    """渲染聊天界面"""
    st.subheader("💬 对话")

    # 会话选择
    sessions_data = _api_get("/api/chat/sessions")
    sessions = sessions_data.get("sessions", []) if sessions_data else []

    # 本地也读一下
    local_sessions = _session_manager.list_sessions()

    all_sessions = {}
    for s in sessions + local_sessions:
        all_sessions[s["id"]] = s

    session_ids = list(all_sessions.keys())

    # 会话选择器
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if session_ids:
            selected = st.selectbox(
                "选择会话",
                options=session_ids,
                format_func=lambda sid: f"{sid}: {all_sessions[sid].get('title', 'Untitled')[:30]}",
                index=0
                if not st.session_state.current_session
                or st.session_state.current_session not in session_ids
                else session_ids.index(st.session_state.current_session),
            )
            if selected != st.session_state.current_session:
                st.session_state.current_session = selected
                st.session_state.chat_messages = []
                st.rerun()
        else:
            st.session_state.current_session = ""
            st.info("暂无会话，发送消息创建新会话")
    with col2:
        if st.button("🆕 新会话", use_container_width=True):
            st.session_state.current_session = ""
            st.session_state.chat_messages = []
            st.rerun()
    with col3:
        if st.button("🗑️ 删除", use_container_width=True) and st.session_state.current_session:
            _api_delete(f"/api/chat/session/{st.session_state.current_session}")
            st.session_state.current_session = ""
            st.session_state.chat_messages = []
            st.rerun()

    # 加载历史消息
    if st.session_state.current_session:
        history_data = _api_get(f"/api/chat/history/{st.session_state.current_session}")
        if history_data:
            messages = history_data.get("messages", [])
            # 只显示 user 和 assistant 消息（隐藏 tool 消息）
            display_messages = [
                m for m in messages if m.get("role") in ("user", "assistant") and m.get("content")
            ]
            st.session_state.chat_messages = [
                {"role": m["role"], "content": m["content"]} for m in display_messages
            ]

    # 显示消息
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入框
    if prompt := st.chat_input("输入消息..."):
        # 显示用户消息
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用 API
        with st.chat_message("assistant"), st.spinner("思考中..."):
            result = _api_post(
                "/api/chat/",
                {
                    "message": prompt,
                    "session_id": st.session_state.current_session,
                },
            )

            if result and "error" in result:
                st.error(f"Error: {result['error']}")
            elif result:
                response = result.get("response", "")
                st.markdown(response)
                st.session_state.current_session = result.get(
                    "session_id", st.session_state.current_session
                )
                st.session_state.chat_messages.append({"role": "assistant", "content": response})

                # 显示工具调用
                tool_calls = result.get("tool_calls", [])
                if tool_calls:
                    with st.expander(f"🔧 调用了 {len(tool_calls)} 个工具"):
                        for tc in tool_calls:
                            st.code(json.dumps(tc, ensure_ascii=False, indent=2), language="json")
            else:
                st.error("无法连接到 API 服务，请确保 API 服务器正在运行")

        st.rerun()


def _api_delete(path: str) -> None:
    """API DELETE 请求"""
    try:
        with httpx.Client(timeout=10.0) as client:
            client.delete(f"{API_BASE_URL}{path}")
    except Exception:
        pass


def _render_task_submit() -> None:
    """渲染任务提交区域"""
    st.subheader("📝 提交任务")

    with st.form("task_form", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            task = st.text_area(
                "任务描述", height=80, placeholder="例如：写一个 Python 函数计算斐波那契数列"
            )
        with col2:
            session_id = st.text_input("会话 ID", value="default")
            submitted = st.form_submit_button("🚀 提交", use_container_width=True)

    if submitted and task:
        with st.spinner("正在提交任务..."):
            result = _api_post("/api/agent/run", {"task": task, "session_id": session_id})
        if result and "error" in result:
            st.error(f"提交失败: {result['error']}")
        elif result:
            task_id = result.get("task_id", "unknown")
            st.success(f"任务已提交！任务 ID: `{task_id}`")
    elif submitted and not task:
        st.warning("请输入任务描述")


def _render_task_queue() -> None:
    """渲染任务队列（实时状态）"""
    st.subheader("📋 任务队列")

    running = _task_store.get_running_tasks()
    if running:
        for task in running:
            with st.status("⏳ 执行中", expanded=True) as status:
                st.write(f"**任务**: {task.get('task', '')}")
                st.write(f"**ID**: `{task.get('id', '')}`")
                plan = task.get("plan", "[]")
                try:
                    plan_list = json.loads(plan) if isinstance(plan, str) else plan
                    st.write(f"**执行计划**: {' → '.join(plan_list)}")
                except Exception:
                    pass
                status.update(label="⏳ 执行中", state="running")
    else:
        st.info("当前没有正在执行的任务")


def _render_execution_history() -> None:
    """渲染执行历史"""
    st.subheader("📜 执行历史")

    tasks = _task_store.list_tasks(limit=20)
    if not tasks:
        st.info("暂无执行历史")
        return

    for task in tasks:
        status = task.get("status", "unknown")
        icon = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        task_id = task.get("id", "")
        task_desc = task.get("task", "")
        created = task.get("created_at", "")
        duration = task.get("duration", 0)

        with st.expander(f"{icon} `{task_id}` — {task_desc[:50]}"):
            st.write(f"**状态**: {status}")
            st.write(f"**创建时间**: {created}")
            if duration:
                st.write(f"**耗时**: {duration:.1f}s")

            # 显示结果
            result_raw = task.get("result", "{}")
            try:
                result = json.loads(result_raw) if isinstance(result_raw, str) else result_raw
                if isinstance(result, dict):
                    plan = result.get("plan", [])
                    if plan:
                        fast_path = result.get("fast_path", False)
                        path_label = " (快速通道)" if fast_path else ""
                        st.write(f"**执行计划**: {' → '.join(plan)}{path_label}")

                    for item in result.get("results", []):
                        agent = item.get("agent", "?")
                        s = item.get("status", "?")
                        a_icon = "✅" if s == "success" else "❌"
                        st.write(f"{a_icon} **{agent}**: {s}")
                        if s == "error":
                            msg = item.get("message", "")
                            if msg:
                                st.error(f"{agent}: {msg[:200]}")
                        if s == "success":
                            r = item.get("result", {})
                            if isinstance(r, dict):
                                # 显示文件保存路径（如果 Coder 写入了文件）
                                output_path = r.get("output_path", "")
                                file_size = r.get("file_size", "")
                                if output_path:
                                    size_str = f" ({file_size} bytes)" if file_size else ""
                                    st.success(f"📁 文件已保存: `{output_path}`{size_str}")

                                code = r.get("generated_code", r.get("test_code", ""))
                                if code:
                                    st.code(str(code)[:800], language="python")
            except Exception:
                st.code(str(result_raw)[:500])

            error = task.get("error", "")
            if error:
                st.error(error)


def _render_metrics() -> None:
    """渲染性能指标（真实数据）"""
    st.subheader("📊 性能指标")

    total = _task_store.get_total_count()
    success = _task_store.get_success_count()
    error = _task_store.get_error_count()
    running = len(_task_store.get_running_tasks())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总任务数", total)
    col2.metric("成功数", success)
    col3.metric("失败数", error)
    col4.metric("执行中", running)


def _render_agent_status() -> None:
    """渲染 Agent 状态（从任务状态推断）"""
    st.sidebar.header("🤖 Agent 状态")

    running_tasks = _task_store.get_running_tasks()
    has_running = len(running_tasks) > 0

    for agent in AGENTS:
        if has_running:
            icon = "✅"
            status_text = "active"
        else:
            icon = "⏸️"
            status_text = "idle"
        st.sidebar.write(f"{icon} {agent}: {status_text}")


def main() -> None:
    """启动可视化面板"""
    st.set_page_config(page_title="Terminal CodingAgent", page_icon="🤖", layout="wide")
    st.title("🤖 Terminal CodingAgent Dashboard")

    # Agent 状态（侧边栏）
    _render_agent_status()

    # 主面板 - 聊天优先
    _render_chat()
    _render_task_submit()
    _render_task_queue()
    _render_execution_history()
    _render_metrics()


if __name__ == "__main__":
    main()
