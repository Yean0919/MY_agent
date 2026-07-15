"""会话管理 - 管理多轮对话历史"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class SessionManager:
    """会话管理器，使用 SQLite 持久化对话历史"""

    def __init__(self, db_path: str = "./data/sessions.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    title TEXT DEFAULT ''
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls TEXT DEFAULT '[]',
                    tool_call_id TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_created
                ON messages(created_at)
            """)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_session(self, title: str = "") -> str:
        """创建新会话

        Args:
            title: 会话标题

        Returns:
            会话 ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title) VALUES (?, ?)",
                (session_id, title),
            )
        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_call_id: str = "",
    ) -> int:
        """添加消息

        Args:
            session_id: 会话 ID
            role: 角色 (user/assistant/system/tool)
            content: 消息内容
            tool_calls: 工具调用列表
            tool_call_id: 工具调用 ID（用于 tool 角色的消息）

        Returns:
            消息 ID
        """
        # 确保会话存在
        self._ensure_session(session_id)

        tool_calls_json = json.dumps(tool_calls, ensure_ascii=False) if tool_calls else "[]"

        with self._conn() as conn:
            cursor = conn.execute(
                """INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, role, content, tool_calls_json, tool_call_id),
            )
            # 更新会话时间
            conn.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )
            return int(cursor.lastrowid or 0)

    def _ensure_session(self, session_id: str) -> None:
        """确保会话存在，不存在则创建"""
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO sessions (id, title) VALUES (?, 'Untitled')",
                    (session_id,),
                )

    def get_history(self, session_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """获取会话历史

        Args:
            session_id: 会话 ID
            limit: 最多返回消息数

        Returns:
            消息列表
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """SELECT role, content, tool_calls, tool_call_id, created_at
                   FROM messages
                   WHERE session_id = ?
                   ORDER BY created_at ASC
                   LIMIT ?""",
                (session_id, limit),
            )
            messages = []
            for row in cursor.fetchall():
                role, content, tool_calls_json, tool_call_id, created_at = row
                tool_calls = json.loads(tool_calls_json) if tool_calls_json else []
                messages.append(
                    {
                        "role": role,
                        "content": content,
                        "tool_calls": tool_calls,
                        "tool_call_id": tool_call_id,
                        "created_at": created_at,
                    }
                )
            return messages

    def list_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        """列出所有会话

        Args:
            limit: 最多返回数

        Returns:
            会话列表
        """
        with self._conn() as conn:
            cursor = conn.execute(
                """SELECT s.id, s.title, s.created_at, s.updated_at,
                          COUNT(m.id) as message_count
                   FROM sessions s
                   LEFT JOIN messages m ON s.id = m.session_id
                   GROUP BY s.id
                   ORDER BY s.updated_at DESC
                   LIMIT ?""",
                (limit,),
            )
            return [
                {
                    "id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "message_count": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            会话信息或 None
        """
        with self._conn() as conn:
            cursor = conn.execute(
                "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
            }

    def update_session_title(self, session_id: str, title: str) -> None:
        """更新会话标题

        Args:
            session_id: 会话 ID
            title: 新标题
        """
        with self._conn() as conn:
            conn.execute(
                "UPDATE sessions SET title = ? WHERE id = ?",
                (title, session_id),
            )

    def delete_session(self, session_id: str) -> bool:
        """删除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否成功删除
        """
        with self._conn() as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

    def get_message_count(self, session_id: str) -> int:
        """获取会话消息数

        Args:
            session_id: 会话 ID

        Returns:
            消息数
        """
        with self._conn() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (session_id,),
            )
            return int(cursor.fetchone()[0])
