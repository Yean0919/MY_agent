"""短期记忆 - LangGraph Checkpointer"""

import json
import sqlite3
from pathlib import Path

from src.core.exceptions import MemoryError
from src.core.state import AgentState


class Checkpointer:
    """短期记忆，使用 SQLite 实现会话断点恢复"""

    def __init__(self, db_path: str = "./data/checkpoints.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON checkpoints(session_id)
            """)

    async def save_checkpoint(self, session_id: str, state: AgentState) -> str:
        """保存检查点

        Args:
            session_id: 会话 ID
            state: Agent 状态

        Returns:
            检查点 ID

        Raises:
            MemoryError: 保存失败
        """
        if not session_id:
            raise MemoryError("Session ID cannot be empty")

        checkpoint_id = f"checkpoint_{session_id}_{self.db_path.stat().st_mtime}"
        state_json = json.dumps(state.to_dict(), ensure_ascii=False)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO checkpoints (session_id, checkpoint_id, state) VALUES (?, ?, ?)",
                    (session_id, checkpoint_id, state_json),
                )
        except Exception as e:
            raise MemoryError(f"Failed to save checkpoint: {e}") from e

        return checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> AgentState | None:
        """加载检查点

        Args:
            checkpoint_id: 检查点 ID

        Returns:
            Agent 状态或 None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT state FROM checkpoints WHERE checkpoint_id = ?",
                    (checkpoint_id,),
                )
                row = cursor.fetchone()
                if row:
                    state_dict = json.loads(row[0])
                    return AgentState.from_dict(state_dict)
        except Exception as e:
            raise MemoryError(f"Failed to load checkpoint: {e}") from e

        return None

    async def list_checkpoints(self, session_id: str) -> list[str]:
        """列出会话的所有检查点

        Args:
            session_id: 会话 ID

        Returns:
            检查点 ID 列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT checkpoint_id FROM checkpoints WHERE session_id = ? ORDER BY created_at DESC",
                    (session_id,),
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise MemoryError(f"Failed to list checkpoints: {e}") from e

    async def delete_checkpoint(self, checkpoint_id: str) -> None:
        """删除检查点

        Args:
            checkpoint_id: 检查点 ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM checkpoints WHERE checkpoint_id = ?",
                    (checkpoint_id,),
                )
        except Exception as e:
            raise MemoryError(f"Failed to delete checkpoint: {e}") from e
