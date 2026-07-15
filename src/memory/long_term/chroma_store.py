"""长期记忆 - ChromaDB 向量存储"""

from pathlib import Path
from typing import Any

from src.core.exceptions import MemoryError


class ChromaStore:
    """长期记忆，使用 ChromaDB 向量库存储知识"""

    def __init__(self, persist_dir: str = "./data/chroma", collection_name: str = "knowledge"):
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None
        self._initialized = False

    def initialize(self) -> None:
        """初始化 ChromaDB"""
        try:
            import chromadb
        except ImportError as e:
            raise MemoryError("chromadb not installed. Run: pip install chromadb") from e

        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self._collection = self._client.get_or_create_collection(self.collection_name)
        self._initialized = True

    def _ensure_initialized(self) -> None:
        """确保已初始化"""
        if not self._initialized:
            self.initialize()

    async def store(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """存储知识

        Args:
            content: 知识内容
            metadata: 元数据

        Returns:
            文档 ID

        Raises:
            MemoryError: 存储失败
        """
        if not content:
            raise MemoryError("Content cannot be empty")

        self._ensure_initialized()

        try:
            # 生成文档 ID
            doc_id = f"doc_{hash(content) % 1000000}"

            # 存储到 ChromaDB
            self._collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id],
            )

            return doc_id
        except Exception as e:
            raise MemoryError(f"Failed to store knowledge: {e}") from e

    async def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """搜索相关知识

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            搜索结果列表

        Raises:
            MemoryError: 搜索失败
        """
        if not query:
            raise MemoryError("Query cannot be empty")

        self._ensure_initialized()

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
            )

            # 格式化结果
            formatted_results = []
            for i in range(len(results.get("ids", [[]])[0])):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i]
                        if results.get("distances")
                        else None,
                    }
                )

            return formatted_results
        except Exception as e:
            raise MemoryError(f"Failed to search knowledge: {e}") from e

    async def delete(self, doc_id: str) -> None:
        """删除知识

        Args:
            doc_id: 文档 ID

        Raises:
            MemoryError: 删除失败
        """
        self._ensure_initialized()

        try:
            self._collection.delete(ids=[doc_id])
        except Exception as e:
            raise MemoryError(f"Failed to delete knowledge: {e}") from e

    async def count(self) -> int:
        """获取文档数量

        Returns:
            文档数量
        """
        self._ensure_initialized()
        return int(self._collection.count())
