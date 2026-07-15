"""请求/响应模型"""

from typing import Any

from pydantic import BaseModel


class AgentRequest(BaseModel):
    """Agent 请求模型"""

    task: str
    session_id: str = ""
    context: dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Agent 响应模型"""

    result: str
    session_id: str
    metadata: dict[str, Any] = {}


class MemoryResponse(BaseModel):
    """记忆响应模型"""

    status: str
    content: str = ""
    doc_id: str = ""


class SearchResponse(BaseModel):
    """搜索响应模型"""

    results: list[dict[str, Any]] = []
    count: int = 0


class IndexResponse(BaseModel):
    """索引响应模型"""

    status: str
    file_path: str = ""
    symbols: list[dict[str, Any]] = []


class ToolResponse(BaseModel):
    """工具响应模型"""

    result: dict[str, Any] = {}
    error: str = ""
