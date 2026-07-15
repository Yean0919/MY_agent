"""类型别名"""

from collections.abc import Callable, Coroutine
from typing import Any

# Agent 状态类型
AgentStateDict = dict[str, Any]

# 消息类型
Message = dict[str, Any]
Messages = list[Message]

# 工具类型
Tool = dict[str, Any]
Tools = list[Tool]

# 回调类型
Callback = Callable[..., Any]
AsyncCallback = Callable[..., Coroutine[Any, Any, Any]]
