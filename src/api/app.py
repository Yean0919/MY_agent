"""FastAPI 应用"""

from typing import Any

from fastapi import FastAPI

from src.api.routes import agent, chat, health, indexing, memory, tools

app = FastAPI(
    title="Terminal CodingAgent API",
    description="Python 原生 Agent Harness API",
    version="0.1.0",
)

# 注册路由
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(indexing.router, prefix="/api/indexing", tags=["indexing"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])


@app.get("/")
async def root() -> dict[str, Any]:
    """根路径"""
    return {"message": "Terminal CodingAgent API", "version": "0.1.0"}
