"""索引路由"""

from pathlib import Path
from typing import Any

from fastapi import APIRouter

from src.indexing.hybrid import HybridIndexer

router = APIRouter()

# 模块级索引器实例
_indexer: HybridIndexer | None = None


def _get_indexer() -> HybridIndexer:
    """获取或创建索引器实例（单例）"""
    global _indexer
    if _indexer is None:
        _indexer = HybridIndexer(str(Path.cwd()))
    return _indexer


@router.post("/index")
async def index_file(file_path: str) -> dict[str, Any]:
    """索引文件

    Args:
        file_path: 文件路径

    Returns:
        索引结果
    """
    if not file_path:
        return {"status": "error", "error": "file_path is required"}

    try:
        indexer = _get_indexer()
        result = await indexer.index_file(file_path)
        return {"status": "indexed", "file_path": file_path, **result}
    except FileNotFoundError as e:
        return {"status": "error", "file_path": file_path, "error": str(e)}
    except Exception as e:
        return {"status": "error", "file_path": file_path, "error": str(e)}


@router.get("/search")
async def search_symbols(query: str, symbol_type: str | None = None) -> dict[str, Any]:
    """搜索符号

    Args:
        query: 查询文本
        symbol_type: 符号类型过滤

    Returns:
        搜索结果
    """
    if not query:
        return {"results": [], "query": query, "count": 0}

    try:
        indexer = _get_indexer()
        results = await indexer.search(query, symbol_type=symbol_type)
        return {"results": results, "query": query, "count": len(results)}
    except Exception as e:
        return {"results": [], "query": query, "count": 0, "error": str(e)}


@router.get("/context")
async def get_context(file_path: str, line: int, token_budget: int = 1000) -> dict[str, Any]:
    """获取上下文

    Args:
        file_path: 文件路径
        line: 行号
        token_budget: Token 预算

    Returns:
        上下文
    """
    if not file_path:
        return {
            "context": "",
            "file_path": file_path,
            "line": line,
            "error": "file_path is required",
        }

    try:
        indexer = _get_indexer()
        symbol_info = await indexer.get_symbol_info(file_path, line, 0)
        return {
            "context": str(symbol_info),
            "file_path": file_path,
            "line": line,
            "symbol_info": symbol_info,
        }
    except Exception as e:
        return {"context": "", "file_path": file_path, "line": line, "error": str(e)}
