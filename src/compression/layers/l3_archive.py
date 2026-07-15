"""L3 归档层 - 长期存储"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast


class L3Archive:
    """L3 归档层，将旧消息归档到长期存储"""

    def __init__(self, archive_path: str = "./data/archive"):
        self.archive_path = Path(archive_path)
        self.archive_path.mkdir(parents=True, exist_ok=True)

    async def archive(self, messages: list[dict[str, Any]], session_id: str) -> str:
        """归档消息

        Args:
            messages: 消息列表
            session_id: 会话 ID

        Returns:
            归档 ID
        """
        if not messages:
            return ""

        # 生成归档 ID
        archive_id = f"archive_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 创建归档文件
        archive_file = self.archive_path / f"{archive_id}.json"

        # 写入归档
        archive_data = {
            "archive_id": archive_id,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages,
        }

        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)

        return archive_id

    async def retrieve(self, archive_id: str) -> list[dict[str, Any]]:
        """检索归档消息

        Args:
            archive_id: 归档 ID

        Returns:
            消息列表
        """
        archive_file = self.archive_path / f"{archive_id}.json"

        if not archive_file.exists():
            return []

        with open(archive_file, encoding="utf-8") as f:
            archive_data = json.load(f)

        return cast(list[dict[str, Any]], archive_data.get("messages", []))

    async def list_archives(self, session_id: str) -> list[str]:
        """列出会话的所有归档

        Args:
            session_id: 会话 ID

        Returns:
            归档 ID 列表
        """
        archives = []
        for archive_file in self.archive_path.glob(f"archive_{session_id}_*.json"):
            archive_id = archive_file.stem
            archives.append(archive_id)

        return sorted(archives, reverse=True)

    async def delete_archive(self, archive_id: str) -> None:
        """删除归档

        Args:
            archive_id: 归档 ID
        """
        archive_file = self.archive_path / f"{archive_id}.json"
        if archive_file.exists():
            archive_file.unlink()

    async def get_archive_stats(self, archive_id: str) -> dict[str, Any]:
        """获取归档统计信息

        Args:
            archive_id: 归档 ID

        Returns:
            统计信息
        """
        archive_file = self.archive_path / f"{archive_id}.json"

        if not archive_file.exists():
            return {}

        with open(archive_file, encoding="utf-8") as f:
            archive_data = json.load(f)

        return {
            "archive_id": archive_id,
            "session_id": archive_data.get("session_id", ""),
            "created_at": archive_data.get("created_at", ""),
            "message_count": archive_data.get("message_count", 0),
            "file_size": archive_file.stat().st_size,
        }
