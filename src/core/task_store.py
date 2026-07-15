"""任务状态管理 - SQLite 持久化"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class TaskStore:
    """任务队列与执行历史，使用 SQLite 持久化"""

    def __init__(self, db_path: str = "./data/tasks.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL DEFAULT '',
                    task TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    plan TEXT DEFAULT '[]',
                    result TEXT DEFAULT '{}',
                    error TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    duration REAL DEFAULT 0.0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON tasks(session_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status
                ON tasks(status)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON tasks(created_at)
            """)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def submit(self, task: str, session_id: str = "") -> str:
        """提交新任务

        Args:
            task: 任务描述
            session_id: 会话 ID

        Returns:
            任务 ID
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO tasks (id, session_id, task, status) VALUES (?, ?, ?, 'pending')",
                (task_id, session_id, task),
            )
        return task_id

    def update_status(self, task_id: str, status: str) -> None:
        """更新任务状态

        Args:
            task_id: 任务 ID
            status: 新状态 (pending|running|success|error)
        """
        with self._conn() as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, task_id),
            )

    def update_plan(self, task_id: str, plan: list[str]) -> None:
        """更新任务执行计划

        Args:
            task_id: 任务 ID
            plan: Agent 执行顺序
        """
        with self._conn() as conn:
            conn.execute(
                "UPDATE tasks SET plan = ? WHERE id = ?",
                (json.dumps(plan, ensure_ascii=False), task_id),
            )

    def update_result(self, task_id: str, result: dict[str, Any], duration: float = 0.0) -> None:
        """更新任务结果

        Args:
            task_id: 任务 ID
            result: 结果字典
            duration: 执行耗时（秒）
        """
        with self._conn() as conn:
            conn.execute(
                "UPDATE tasks SET result = ?, duration = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (json.dumps(result, ensure_ascii=False, default=str), duration, task_id),
            )

    def update_error(self, task_id: str, error: str) -> None:
        """更新任务错误信息

        Args:
            task_id: 任务 ID
            error: 错误信息
        """
        with self._conn() as conn:
            conn.execute(
                "UPDATE tasks SET error = ?, status = 'error', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (error, task_id),
            )

    def get_by_id(self, task_id: str) -> dict[str, Any] | None:
        """按 ID 获取任务

        Args:
            task_id: 任务 ID

        Returns:
            任务字典或 None
        """
        with self._conn() as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row, strict=True))

    def list_tasks(
        self,
        session_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """列出任务

        Args:
            session_id: 按会话过滤
            status: 按状态过滤
            limit: 最多返回数

        Returns:
            任务列表（按创建时间倒序）
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[Any] = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._conn() as conn:
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]

    def get_running_tasks(self) -> list[dict[str, Any]]:
        """获取正在执行的任务

        Returns:
            运行中的任务列表
        """
        return self.list_tasks(status="running")

    def get_stats(self) -> dict[str, int]:
        """获取任务统计

        Returns:
            各状态任务数量
        """
        with self._conn() as conn:
            cursor = conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            return dict(cursor.fetchall())

    def get_total_count(self) -> int:
        """获取总任务数

        Returns:
            总任务数
        """
        with self._conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM tasks")
            return int(cursor.fetchone()[0])

    def get_success_count(self) -> int:
        """获取成功任务数

        Returns:
            成功任务数
        """
        with self._conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'success'")
            return int(cursor.fetchone()[0])

    def get_error_count(self) -> int:
        """获取失败任务数

        Returns:
            失败任务数
        """
        with self._conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'error'")
            return int(cursor.fetchone()[0])
