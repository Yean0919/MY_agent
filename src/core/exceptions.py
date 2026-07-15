"""自定义异常"""


class AgentError(Exception):
    """Agent 相关异常基类"""

    pass


class LoopError(AgentError):
    """循环相关异常"""

    pass


class MemoryError(AgentError):
    """记忆相关异常"""

    pass


class IndexingError(AgentError):
    """索引相关异常"""

    pass


class ToolError(AgentError):
    """工具相关异常"""

    pass
