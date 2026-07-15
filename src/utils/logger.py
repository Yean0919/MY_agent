"""structlog 日志配置"""

from typing import Any

import structlog


def get_logger(name: str = "tca") -> "structlog.stdlib.BoundLogger | Any":
    """获取日志记录器

    Args:
        name: 日志名称

    Returns:
        日志记录器
    """
    return structlog.get_logger(name)
