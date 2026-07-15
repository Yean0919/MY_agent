"""MCP 语言桥接 - stdio/SSE 协议支持"""

import subprocess
from typing import Any, cast


class MCPBridge:
    """MCP 语言桥接，支持 stdio 和 SSE 协议"""

    def __init__(self, transport: str = "stdio"):
        if transport not in ("stdio", "sse"):
            raise ValueError(f"Unsupported transport: {transport}")
        self.transport = transport
        self._process: subprocess.Popen[bytes] | None = None

    async def create_connection(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> Any:
        """创建连接

        Args:
            command: 命令
            args: 参数
            env: 环境变量

        Returns:
            连接对象
        """
        if self.transport == "stdio":
            return await self._create_stdio_connection(command, args, env)
        else:
            # TODO: 实现 SSE 连接
            return None

    async def _create_stdio_connection(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.Popen[bytes]:
        """创建 stdio 连接

        Args:
            command: 命令
            args: 参数
            env: 环境变量

        Returns:
            进程对象
        """
        full_env = dict(__import__("os").environ)
        if env:
            full_env.update(env)

        self._process = subprocess.Popen(
            [command] + (args or []),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
        )

        return self._process

    async def send_message(self, connection: Any, message: dict[str, Any]) -> None:
        """发送消息

        Args:
            connection: 连接对象
            message: 消息
        """
        if self.transport == "stdio" and isinstance(connection, subprocess.Popen):
            import json

            message_json = json.dumps(message) + "\n"
            assert connection.stdin is not None
            connection.stdin.write(message_json.encode("utf-8"))
            connection.stdin.flush()

    async def receive_message(self, connection: Any) -> dict[str, Any] | None:
        """接收消息

        Args:
            connection: 连接对象

        Returns:
            消息或 None
        """
        if self.transport == "stdio" and isinstance(connection, subprocess.Popen):
            assert connection.stdout is not None
            line = connection.stdout.readline()
            if line:
                import json

                return cast(dict[str, Any], json.loads(line.decode("utf-8")))
        return None

    async def close_connection(self, connection: Any) -> None:
        """关闭连接

        Args:
            connection: 连接对象
        """
        if isinstance(connection, subprocess.Popen):
            connection.terminate()
            connection.wait()
            self._process = None
