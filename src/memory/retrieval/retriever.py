"""记忆检索策略"""

from typing import Any

from src.core.exceptions import MemoryError
from src.memory.long_term.chroma_store import ChromaStore


class MemoryRetriever:
    """记忆检索器，实现多种检索策略"""

    def __init__(self, chroma_store: ChromaStore):
        self.store = chroma_store

    async def retrieve_by_similarity(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """基于相似度的检索

        Args:
            query: 查询文本
            top_k: 返回结果数
            threshold: 相似度阈值

        Returns:
            检索结果列表

        Raises:
            MemoryError: 检索失败
        """
        if not query:
            raise MemoryError("Query cannot be empty")

        results = await self.store.search(query, top_k)

        # 过滤低于阈值的结果
        filtered_results = []
        for r in results:
            distance = r.get("distance", 1.0)
            # ChromaDB 使用 L2 距离，距离越小越相似
            # 转换为相似度分数 (0-1)
            similarity = 1.0 / (1.0 + distance)
            if similarity >= threshold:
                r["similarity"] = similarity
                filtered_results.append(r)

        return filtered_results

    async def retrieve_by_metadata(
        self,
        metadata_filter: dict[str, Any],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """基于元数据的检索

        Args:
            metadata_filter: 元数据过滤条件
            top_k: 返回结果数

        Returns:
            检索结果列表
        """
        # TODO: 实现元数据检索
        # ChromaDB 支持 where 子句进行元数据过滤
        return []

    async def retrieve_hybrid(
        self,
        query: str,
        metadata_filter: dict[str, Any] | None = None,
        top_k: int = 5,
        similarity_weight: float = 0.7,
    ) -> list[dict[str, Any]]:
        """混合检索（相似度 + 元数据）

        Args:
            query: 查询文本
            metadata_filter: 元数据过滤条件
            top_k: 返回结果数
            similarity_weight: 相似度权重

        Returns:
            检索结果列表
        """
        # 先进行相似度检索
        similarity_results = await self.retrieve_by_similarity(query, top_k * 2)

        # 如果有元数据过滤，进一步过滤
        if metadata_filter:
            filtered_results = []
            for r in similarity_results:
                metadata = r.get("metadata", {})
                match = True
                for key, value in metadata_filter.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(r)
            similarity_results = filtered_results

        # 按相似度排序，取前 top_k
        similarity_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return similarity_results[:top_k]
