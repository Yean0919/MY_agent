"""CLI entry point — 交互式编程助手。

终端交互统一走 Harness（AgentLoop / TAOR 循环），由 LLM 自己决定
是直接回复还是调用工具，不再手动路由（闲聊/解释/工具分流）。

Usage:
    # 交互模式
    yean

    # 单次执行
    yean "write a fibonacci function"

    # 指定会话
    yean --session my_project "refactor the auth module"

    # 指定工作目录
    yean --cwd /path/to/project "explain this codebase"
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import click

from src.agents.orchestrator import Orchestrator
from src.agents.roles.coder import CoderAgent
from src.agents.roles.researcher import ResearcherAgent
from src.agents.roles.reviewer import ReviewerAgent
from src.agents.roles.tester import TesterAgent
from src.config.settings import get_settings
from src.harness.engine import run_agent
from src.memory.short_term.session_state import SessionState
from src.tools.registry import ToolRegistry

# ── 常量 ────────────────────────────────────────────────────────────────────

VERSION = "v0.1.0"
PRODUCT = "YEAN"

# 终端宽度
_TERM_WIDTH = shutil.get_terminal_size().columns

# 界面固定宽度（收窄，不随终端拉伸）
UI_WIDTH = 80


# ── YEAN 艺术字 logo（Unicode 块字符，粗体 3D 风格）───────────────────────

_YEAN_ART = [
    "               ██╗   ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗",
    "               ██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔══██╗██╔════╝",
    "               ██║   ██║█████╗  ██║   ██║██║  ██║██████╔╝█████╗  ",
    "               ╚██╗ ██╔╝██╔══╝  ██║   ██║██║  ██║██╔══██╗██╔══╝  ",
    "                ╚████╔╝ ███████╗╚██████╔╝██████╔╝██║  ██║███████╗",
    "                 ╚═══╝  ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝",
]

# 副标题
_SUBTITLE = "Terminal Coding Agent"
_TAGLINE = "Multi-Agent 协作 · 跨会话记忆 · 代码索引 · MCP 接入"


def _center(text: str, width: int) -> str:
    """居中文字（考虑 CJK 字符占 2 列宽）。"""
    visual_len = 0
    for ch in text:
        if ord(ch) > 0x2E80:
            visual_len += 2
        else:
            visual_len += 1
    pad = max(0, (width - visual_len) // 2)
    return " " * pad + text


def _build_welcome(settings) -> str:
    """构建 YEAN 艺术字欢迎界面（固定宽度）。"""
    width = UI_WIDTH

    lines: list[str] = []

    # ── 顶部装饰线 ──
    lines.append("")
    lines.append("  " + "█" * (width - 4))
    lines.append("  " + "█" + " " * (width - 4) + "█")

    # ── YEAN 艺术字（居中）──
    for art_line in _YEAN_ART:
        lines.append("  " + _center(art_line, width - 4))

    # ── 副标题 ──
    lines.append("  " + "█" + " " * (width - 4) + "█")
    lines.append("  " + _center(_SUBTITLE, width - 4))
    lines.append("  " + _center(f"({VERSION})", width - 4))
    lines.append("  " + _center(_TAGLINE, width - 4))
    lines.append("  " + "█" + " " * (width - 4) + "█")

    # ── 状态信息 ──
    provider = settings.llm.default_provider
    model = settings.llm.default_model
    cwd = str(Path.cwd())
    lines.append("  " + "█" + " " * (width - 4) + "█")
    lines.append("  " + "█" + f"  Model: {model}".ljust(width - 4) + "█")
    lines.append("  " + "█" + f"  Provider: {provider}".ljust(width - 4) + "█")
    lines.append("  " + "█" + f"  CWD: {cwd}".ljust(width - 4) + "█")
    lines.append("  " + "█" + " " * (width - 4) + "█")

    # ── 底部装饰线 ──
    lines.append("  " + "█" * (width - 4))
    lines.append("")

    return "\n".join(lines)


def _print_welcome(settings) -> None:
    """打印 YEAN 欢迎界面。"""
    click.echo(_build_welcome(settings))


# ── 内置命令 ───────────────────────────────────────────────────────────────


def _show_tools(tool_registry: ToolRegistry) -> None:
    """显示可用工具。"""
    click.echo("\n[Tools] 可用工具:")
    for tool in tool_registry.list_tools():
        name = tool.get("name", "?")
        desc = tool.get("description", "")
        click.echo(f"  - {name}: {desc}")


def _show_agents(orchestrator: Orchestrator) -> None:
    """显示已注册 Agent。"""
    click.echo("\n[Agents] 已注册 Agent:")
    for name in orchestrator.list_agents():
        agent = orchestrator.get_agent(name)
        desc = agent.description if agent else ""
        click.echo(f"  - {name}: {desc}")


def _show_status(session_state: SessionState, settings) -> None:
    """显示会话状态。"""
    click.echo("\n[Status] 会话状态:")
    click.echo(f"  Session: {session_state.session_id}")
    click.echo(f"  History: {session_state.get_history_count()} messages")
    click.echo(f"  Provider: {settings.llm.default_provider}")
    click.echo(f"  Model: {settings.llm.default_model}")
    click.echo(f"  CWD: {Path.cwd()}")


def _show_memory(session_state: SessionState) -> None:
    """显示会话记忆（短期）。"""
    history = session_state.get_history()
    if history:
        click.echo(f"\n[Memory] 会话记忆 ({len(history)} 条):")
        for i, h in enumerate(history[-10:], 1):
            task = h.task or "(no task)"
            click.echo(f"  {i}. {task[:80]}")
    else:
        click.echo("\n[Memory] 暂无会话记忆")


def _save_memory(session_state: SessionState, text: str) -> None:
    """提取并保存记忆（'记住: xxx' 模式）。"""
    for m in re.finditer(r"记住[：:]\s*(.+)", text):
        content = m.group(1).strip()
        session_state.update(
            {
                "memory_references": [
                    *(getattr(session_state.state, "memory_references", []) or []),
                    {"content": content, "saved_at": datetime.now(timezone.utc).isoformat()},
                ]
            }
        )


# ── Agent 执行（多 Agent 编排，agents 命令用）────────────────────────────


def _build_orchestrator() -> Orchestrator:
    """构建并注册 Agent 的编排器。"""
    orchestrator = Orchestrator()
    orchestrator.register_agent(CoderAgent())
    orchestrator.register_agent(ReviewerAgent())
    orchestrator.register_agent(TesterAgent())
    orchestrator.register_agent(ResearcherAgent())
    return orchestrator


# ── 配置检查 ───────────────────────────────────────────────────────────────


def _check_credentials(settings) -> str | None:
    """检查 LLM 凭证是否配置，返回错误信息或 None。"""
    api_key = settings.openai.api_key
    api_key_val = api_key.get_secret_value() if api_key else ""

    if not api_key_val:
        return (
            "LLM API Key 未配置。\n"
            "请在 .env 文件中设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY，\n"
            "或运行: yean --help 查看配置说明。"
        )
    return None


# ── CLI 命令 ───────────────────────────────────────────────────────────────


@click.command()
@click.argument("prompt", required=False)
@click.option("--session", "-s", default="cli", help="Session ID")
@click.option("--cwd", "-d", default=None, help="工作目录")
@click.option("--provider", "-p", default=None, help="LLM provider")
@click.option("--model", "-m", default=None, help="Model name")
@click.option("--log-level", default=None, help="Log level")
def cli(
    prompt: str | None,
    session: str,
    cwd: str | None,
    provider: str | None,
    model: str | None,
    log_level: str | None,
) -> None:
    """YEAN - Multi-Agent Terminal Coding Agent."""
    settings = get_settings()
    if log_level:
        settings.log_level = log_level
    if provider:
        settings.llm.default_provider = provider  # type: ignore[assignment]
    if model:
        settings.llm.default_model = model

    if cwd:
        Path(cwd).mkdir(parents=True, exist_ok=True)
        os.chdir(cwd)

    project_root = str(Path.cwd())

    if prompt:
        asyncio.run(_single_shot(prompt, session, settings, project_root))
    else:
        asyncio.run(_interactive(session, settings, project_root))


async def _single_shot(prompt: str, session: str, settings, project_root: str) -> None:
    """单次执行模式 — 走 Harness。"""
    click.echo(f"> {prompt}\n")

    reply, tool_results, metadata = await run_agent(prompt, session, project_root)

    for tr in tool_results:
        status = "OK" if tr.get("success") else "ERR"
        click.echo(f"[{status}] {tr['tool']}: {tr['result'][:200]}")

    click.echo(f"\n{reply}")
    click.echo(
        f"\n[Meta] tools: {metadata.get('tool_calls', 0)}, time: {metadata.get('duration', 0):.1f}s"
    )


async def _interactive(session: str, settings, project_root: str) -> None:
    """交互模式 — 所有输入统一走 Harness（AgentLoop）。"""
    _print_welcome(settings)

    # 检查凭证
    cred_error = _check_credentials(settings)
    if cred_error:
        click.echo(f"[Warning] {cred_error}")
        click.echo()

    orchestrator = _build_orchestrator()
    tool_registry = ToolRegistry()
    session_state = SessionState(session_id=session)

    # 加载 MCP（可选）
    try:
        from src.tools.mcp.server_registry import MCPServerRegistry

        mcp_registry = MCPServerRegistry()
        tool_registry.set_mcp_registry(mcp_registry)
    except Exception as e:
        click.echo(f"[Warning] MCP load failed (ignored): {e}")

    # 会话历史（user/assistant 消息对，传给 AgentLoop 做上下文）
    history: list[dict[str, str]] = []

    click.echo()
    click.echo("Commands: quit/exit  memory  clear  tools  agents  status  help")
    click.echo("-" * UI_WIDTH)

    while True:
        try:
            # 用 input() 代替 click.prompt()，避免自动回显导致重复
            user_input = input("\nUser> ")
        except (KeyboardInterrupt, EOFError):
            click.echo("\nBye!")
            break

        # 清理输入中的 surrogate 字符（管道输入时编码问题）
        user_input = "".join(ch for ch in user_input if not (0xDC00 <= ord(ch) <= 0xDFFF))

        if not user_input.strip():
            continue

        cmd = user_input.strip().lower()

        # 特殊命令
        if cmd in ("quit", "exit", "q"):
            click.echo("Bye!")
            break

        if cmd == "memory":
            _show_memory(session_state)
            continue

        if cmd == "clear":
            history.clear()
            session_state.clear_history()
            click.echo("[OK] Session cleared")
            continue

        if cmd == "tools":
            _show_tools(tool_registry)
            continue

        if cmd == "agents":
            _show_agents(orchestrator)
            continue

        if cmd == "status":
            _show_status(session_state, settings)
            continue

        if cmd in ("help", "h"):
            _print_welcome(settings)
            continue

        # ── 所有非命令输入统一走 Harness ──────────────────────────────
        click.echo("Assistant> ", nl=False)
        try:
            reply, tool_results, metadata = await run_agent(
                user_input, session, project_root, history
            )

            # 显示工具结果（如有）
            for tr in tool_results:
                status = "OK" if tr.get("success") else "ERR"
                click.echo(f"\n[{status}] {tr['tool']}: {tr['result'][:300]}")

            # 显示回复
            click.echo(f"\n{reply}")

            # 显示元数据
            if tool_results:
                click.echo(
                    f"\n[Meta] tools: {metadata.get('tool_calls', 0)}, "
                    f"time: {metadata.get('duration', 0):.1f}s"
                )

            # 保存历史
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})

            # 保存会话状态 + 记忆
            session_state.update({"task": user_input, "messages": [reply]})
            _save_memory(session_state, user_input)

        except Exception as e:
            click.echo(f"\n[Error] {e}")


if __name__ == "__main__":
    cli()
