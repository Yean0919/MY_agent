"""Tool system using langchain native tools.

为 AgentLoop 提供结构化工具调用（read_file / write_file / edit_file /
list_dir / grep / find_files），替代旧的手动 _TOOL_PATTERNS 路由。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """工具执行错误（用于路径逃逸等需要向上抛出的场景）。"""

    pass


def _safe_path(base: str, target: str) -> Path:
    """Resolve target relative to base, preventing directory escape."""
    base = Path(base).resolve()
    target_path = Path(target)

    if target_path.is_absolute():
        target_path = target_path.resolve()
        if not str(target_path).startswith(str(base)):
            raise ToolExecutionError(f"Path escape blocked: {target}")
        return target_path

    target_path = (base / target).resolve()
    if not str(target_path).startswith(str(base)):
        raise ToolExecutionError(f"Path escape blocked: {target}")
    return target_path


@tool
def read_file(path: str, base: str = "") -> str:
    """Read file content.

    Args:
        path: File path (relative to base or absolute within project)
        base: Project base directory
    """
    try:
        p = _safe_path(base, path)
        if not p.exists():
            return f"File not found: {path}"
        content = p.read_text(encoding="utf-8")
        if len(content) > 5000:
            return content[:5000] + f"\n... (truncated, {len(content)} chars total)"
        return content
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error reading {path}: {e}"


@tool
def write_file(path: str, content: str, base: str = "") -> str:
    """Write content to a file (creates parent directories).

    Args:
        path: File path (relative to base or absolute within project)
        content: Full file content to write
        base: Project base directory
    """
    try:
        p = _safe_path(base, path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} chars to {path}"
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error writing {path}: {e}"


@tool
def edit_file(path: str, old_text: str, new_text: str, base: str = "") -> str:
    """Replace old_text with new_text in a file.

    Args:
        path: File path
        old_text: Text to find and replace
        new_text: Replacement text
        base: Project base directory
    """
    try:
        p = _safe_path(base, path)
        if not p.exists():
            return f"File not found: {path}"
        src = p.read_text(encoding="utf-8")
        if old_text not in src:
            return f"Text not found in {path}: {old_text[:50]}..."
        new_src = src.replace(old_text, new_text, 1)
        p.write_text(new_src, encoding="utf-8")
        return f"Replaced in {path}"
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error editing {path}: {e}"


@tool
def list_dir(path: str = ".", base: str = "") -> str:
    """List directory contents with type and size.

    Args:
        path: Directory path
        base: Project base directory
    """
    try:
        p = _safe_path(base, path)
        if not p.is_dir():
            return f"Not a directory: {path}"
        entries = []
        for child in sorted(p.iterdir()):
            entry_type = "dir" if child.is_dir() else "file"
            size = child.stat().st_size if child.is_file() else "-"
            entries.append(f"  [{entry_type}] {child.name} ({size})")
        return f"Contents of {path}:\n" + "\n".join(entries)
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error listing {path}: {e}"


@tool
def grep(pattern: str, path: str = ".", glob: str = "*.py", base: str = "") -> str:
    """Search for a regex pattern in files.

    Args:
        pattern: Regex pattern to search for
        path: Directory to search in
        glob: File glob pattern (default: *.py)
        base: Project base directory
    """
    import re

    try:
        root = _safe_path(base, path)
        results = []
        for py in root.rglob(glob):
            try:
                for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
                    if re.search(pattern, line):
                        rel = py.relative_to(root)
                        results.append(f"  {rel}:{i}: {line[:80]}")
            except Exception:
                continue
        if not results:
            return f"No matches for '{pattern}' in {path}"
        return f"Matches for '{pattern}':\n" + "\n".join(results[:50])
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error searching: {e}"


@tool
def find_files(pattern: str = "*", path: str = ".", base: str = "") -> str:
    """Find files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g., *.py, test_*)
        path: Directory to search in
        base: Project base directory
    """
    try:
        root = _safe_path(base, path)
        files = sorted(str(p.relative_to(root)) for p in root.rglob(pattern) if p.is_file())
        if not files:
            return f"No files matching '{pattern}' in {path}"
        return f"Files matching '{pattern}':\n" + "\n".join(f"  {f}" for f in files[:50])
    except ToolExecutionError:
        raise
    except Exception as e:
        return f"Error finding files: {e}"


# Tool registry
TOOLS: dict[str, Any] = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_dir": list_dir,
    "grep": grep,
    "find_files": find_files,
}


def get_tools_list() -> list[Any]:
    """Get list of langchain tools for bind_tools."""
    return list(TOOLS.values())


def get_tool_descriptions() -> list[dict[str, str]]:
    """Get tool descriptions for display."""
    return [{"name": name, "description": tool.description} for name, tool in TOOLS.items()]
