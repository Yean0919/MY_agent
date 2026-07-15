"""MCP 配置管理"""

from pathlib import Path
from typing import Any

import yaml


class MCPConfigManager:
    """MCP 服务器配置管理"""

    def __init__(self, config_path: str = "./config/mcp_servers.yaml"):
        self.config_path = Path(config_path)
        self._configs: list[dict[str, Any]] = []

    def load(self) -> list[dict[str, Any]]:
        """加载配置

        Returns:
            配置列表
        """
        if not self.config_path.exists():
            return []

        with open(self.config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self._configs = data.get("mcp_servers", [])
        return self._configs

    def save(self, configs: list[dict[str, Any]]) -> None:
        """保存配置

        Args:
            configs: 配置列表
        """
        self._configs = configs
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump({"mcp_servers": configs}, f, allow_unicode=True, default_flow_style=False)

    def add_server(self, config: dict[str, Any]) -> None:
        """添加服务器配置

        Args:
            config: 服务器配置
        """
        if "name" not in config:
            raise ValueError("Server config must have 'name' field")

        # 检查是否已存在
        for i, existing in enumerate(self._configs):
            if existing.get("name") == config["name"]:
                self._configs[i] = config
                self.save(self._configs)
                return

        self._configs.append(config)
        self.save(self._configs)

    def remove_server(self, name: str) -> None:
        """移除服务器配置

        Args:
            name: 服务器名称
        """
        self._configs = [c for c in self._configs if c.get("name") != name]
        self.save(self._configs)

    def get_server(self, name: str) -> dict[str, Any] | None:
        """获取服务器配置

        Args:
            name: 服务器名称

        Returns:
            服务器配置或 None
        """
        for config in self._configs:
            if config.get("name") == name:
                return config
        return None

    def list_servers(self) -> list[str]:
        """列出所有服务器名称

        Returns:
            服务器名称列表
        """
        return [c.get("name", "") for c in self._configs if c.get("name")]
