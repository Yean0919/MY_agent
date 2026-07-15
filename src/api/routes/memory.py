"""记忆路由"""

from typing import Any

from fastapi import APIRouter

from src.memory.long_term.knowledge_base import KnowledgeBase

router = APIRouter()

# 模块级知识库实例
_knowledge_base: KnowledgeBase | None = None


def _get_kb() -> KnowledgeBase:
    """获取或创建知识库实例（单例）"""
    global _knowledge_base
    if _knowledge_base is None:
        from src.memory.long_term.chroma_store import ChromaStore

        store = ChromaStore()
        store.initialize()
        _knowledge_base = KnowledgeBase(store)
    return _knowledge_base


@router.post("/store")
async def store_knowledge(content: str, category: str = "general") -> dict[str, Any]:
    """存储知识

    Args:
        content: 知识内容
        category: 分类

    Returns:
        存储结果
    """
    if not content:
        return {"status": "error", "error": "Content cannot be empty"}

    try:
        kb = _get_kb()
        doc_id = await kb.add_knowledge(content, category=category)
        return {"status": "stored", "doc_id": doc_id, "content": content[:100]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/search")
async def search_knowledge(query: str, top_k: int = 5) -> dict[str, Any]:
    """搜索知识

    Args:
        query: 查询文本
        top_k: 返回结果数

    Returns:
        搜索结果
    """
    if not query:
        return {"results": [], "query": query, "count": 0}

    try:
        kb = _get_kb()
        results = await kb.search_knowledge(query, top_k=top_k)
        return {"results": results, "query": query, "count": len(results)}
    except Exception as e:
        return {"results": [], "query": query, "count": 0, "error": str(e)}


@router.get("/stats")
async def get_knowledge_stats() -> dict[str, Any]:
    """获取知识库统计

    Returns:
        统计信息
    """
    try:
        kb = _get_kb()
        stats = await kb.get_knowledge_stats()
        return stats
    except Exception as e:
        return {"error": str(e)}
