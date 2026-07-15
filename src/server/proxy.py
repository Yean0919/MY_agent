"""代理服务器 - 本地 LLM 代理"""

import asyncio
import contextlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from starlette.responses import Response as StarletteResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TCA Proxy Server", version="0.1.0")

# 全局配置
_proxy_config: dict[str, Any] = {
    "host": "127.0.0.1",
    "port": 8081,
    "enabled": False,
    "providers": [],
    "active_provider": None,
}


def load_proxy_config() -> dict[str, Any]:
    """加载代理配置"""
    global _proxy_config
    config_path = Path("./config/proxy_config.json")
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            _proxy_config = json.load(f)
    return _proxy_config


def get_active_provider() -> dict[str, Any] | None:
    """获取激活的提供商"""
    load_proxy_config()
    for provider in _proxy_config.get("providers", []):
        if provider.get("active"):
            return cast(dict[str, Any], provider)
    return None


class ProxyConfig(BaseModel):
    """代理配置"""

    host: str = "127.0.0.1"
    port: int = 8080
    upstream_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    enabled: bool = True


class ProxyServer:
    """代理服务器"""

    def __init__(self, config: ProxyConfig):
        self.config = config
        self._server_task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        """启动代理服务器"""
        import uvicorn

        if self._running:
            logger.warning("Proxy server already running")
            return

        config = uvicorn.Config(app, host=self.config.host, port=self.config.port, log_level="info")
        server = uvicorn.Server(config)
        self._server_task = asyncio.create_task(server.serve())
        self._running = True
        logger.info(f"Proxy server started at http://{self.config.host}:{self.config.port}")

    async def stop(self) -> None:
        """停止代理服务器"""
        if self._server_task:
            self._server_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._server_task
            self._running = False
            logger.info("Proxy server stopped")

    @property
    def is_running(self) -> bool:
        """检查服务器是否运行中"""
        return self._running


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request) -> "StarletteResponse":
    """代理请求到上游 LLM API"""
    # 跳过健康检查和配置端点
    if path in ("health", "config", "status"):
        return JSONResponse(status_code=404, content={"error": "Not found"})

    # 获取激活的提供商
    provider = get_active_provider()
    if not provider:
        return JSONResponse(
            status_code=503,
            content={
                "error": "No active provider configured. Please configure a provider in the GUI."
            },
        )

    # 构建目标 URL
    base_url = provider.get("url", "").rstrip("/")
    # 确保 URL 以 /v1 结尾
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    target_url = f"{base_url}/{path}"

    logger.info(f"Proxying {request.method} {path} -> {target_url}")

    # 获取 API Key
    api_key = provider.get("api_key", "")
    if not api_key:
        return JSONResponse(
            status_code=503,
            content={
                "error": f"API key not configured for provider: {provider.get('name', 'unknown')}"
            },
        )

    # 构建请求头
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("origin", None)
    headers.pop("referer", None)
    headers.pop("connection", None)
    headers["Authorization"] = f"Bearer {api_key}"
    headers["Content-Type"] = "application/json"

    logger.info(f"Proxying {request.method} {path} -> {target_url}")
    logger.info(
        "Headers: " + str({k: "***" if k == "Authorization" else v for k, v in headers.items()})
    )

    # 获取请求体
    body = await request.body()
    logger.info(f"Request body length: {len(body)} bytes")

    # 转发请求
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )

            logger.info(f"Response: {response.status_code}")

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
    except httpx.ConnectError as e:
        logger.error(f"Connection error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"Failed to connect to upstream: {str(e)}"},
        )
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error: {e}")
        return JSONResponse(
            status_code=504,
            content={"error": f"Upstream timeout: {str(e)}"},
        )
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return JSONResponse(
            status_code=502,
            content={"error": f"Proxy error: {str(e)}"},
        )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查"""
    return {"status": "healthy", "service": "TCA Proxy Server"}


@app.get("/config")
async def get_config() -> dict[str, Any]:
    """获取当前配置"""
    load_proxy_config()
    return _proxy_config


@app.get("/status")
async def get_status() -> dict[str, Any]:
    """获取服务器状态"""
    provider = get_active_provider()
    return {
        "running": True,
        "active_provider": provider.get("name") if provider else None,
        "providers_count": len(_proxy_config.get("providers", [])),
    }


@app.post("/start")
async def start_proxy() -> dict[str, Any]:
    """启动代理服务器"""
    load_proxy_config()
    host = _proxy_config.get("proxy", {}).get("host", "127.0.0.1")
    port = _proxy_config.get("proxy", {}).get("port", 8080)

    server = ProxyServer(ProxyConfig(host=host, port=port))
    asyncio.create_task(server.start())

    return {"status": "started", "host": host, "port": port}


@app.post("/stop")
async def stop_proxy() -> dict[str, str]:
    """停止代理服务器"""
    return {"status": "stopped"}


def run_proxy_server(host: str = "127.0.0.1", port: int = 8081) -> None:
    """运行代理服务器"""
    import uvicorn

    logger.info(f"Starting TCA Proxy Server at http://{host}:{port}")
    logger.info("Press Ctrl+C to stop")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_proxy_server()
