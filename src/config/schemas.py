"""配置数据结构"""

from pydantic import BaseModel


class MCPConfig(BaseModel):
    """MCP 服务器配置"""

    name: str
    command: str
    args: list[str] = []
    env: dict[str, str] = {}


class SkillConfig(BaseModel):
    """Skill 配置"""

    name: str
    path: str
    description: str = ""
