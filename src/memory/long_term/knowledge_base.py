"""知识库管理"""

from datetime import datetime
from typing import Any

from src.core.exceptions import MemoryError
from src.memory.long_term.chroma_store import ChromaStore


class KnowledgeBase:
    """知识库管理，封装 ChromaDB 操作"""

    def __init__(self, chroma_store: ChromaStore):
        self.store = chroma_store

    async def add_knowledge(
        self,
        content: str,
        category: str = "general",
        tags: list[str] | None = None,
        source: str = "",
    ) -> str:
        """添加知识

        Args:
            content: 知识内容
            category: 分类
            tags: 标签
            source: 来源

        Returns:
            文档 ID

        Raises:
            MemoryError: 添加失败
        """
        if not content:
            raise MemoryError("Content cannot be empty")

        metadata = {
            "category": category,
            "tags": tags or [],
            "source": source,
            "created_at": datetime.now().isoformat(),
        }

        return await self.store.store(content, metadata)

    async def search_knowledge(
        self,
        query: str,
        category: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """搜索知识

        Args:
            query: 查询文本
            category: 分类过滤
            top_k: 返回结果数

        Returns:
            搜索结果列表
        """
        results = await self.store.search(query, top_k)

        if category:
            results = [r for r in results if r.get("metadata", {}).get("category") == category]

        return results

    async def get_knowledge_stats(self) -> dict[str, Any]:
        """获取知识库统计信息

        Returns:
            统计信息字典
        """
        total = await self.store.count()

        # 按分类统计
        category_stats: dict[str, int] = {}
        # TODO: 实现按分类统计

        return {
            "total_documents": total,
            "categories": category_stats,
            "last_updated": datetime.now().isoformat(),
        }

    async def delete_knowledge(self, doc_id: str) -> None:
        """删除知识

        Args:
            doc_id: 文档 ID
        """
        await self.store.delete(doc_id)
