"""Token 消耗追踪器 - 统计各 Agent/模型的 Token 使用量"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """单次调用的 Token 使用量"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""
    profile: str = ""
    agent: str = ""
    timestamp: float = field(default_factory=time.time)

    @property
    def cost_estimate(self) -> float:
        """估算费用（美元，基于常见定价）"""
        # 粗略估算：输入 $0.003/1K，输出 $0.015/1K（GPT-4 级别）
        return (self.prompt_tokens * 0.003 + self.completion_tokens * 0.015) / 1000


@dataclass
class TokenStats:
    """累计 Token 统计"""

    total_calls: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    by_agent: dict[str, dict[str, int]] = field(default_factory=dict)
    by_model: dict[str, dict[str, int]] = field(default_factory=dict)
    history: list[TokenUsage] = field(default_factory=list)

    def add(self, usage: TokenUsage) -> None:
        """记录一次调用的 Token 使用量"""
        self.total_calls += 1
        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.total_tokens += usage.total_tokens

        # 按 Agent 统计
        if usage.agent:
            if usage.agent not in self.by_agent:
                self.by_agent[usage.agent] = {"calls": 0, "prompt": 0, "completion": 0, "total": 0}
            self.by_agent[usage.agent]["calls"] += 1
            self.by_agent[usage.agent]["prompt"] += usage.prompt_tokens
            self.by_agent[usage.agent]["completion"] += usage.completion_tokens
            self.by_agent[usage.agent]["total"] += usage.total_tokens

        # 按模型统计
        if usage.model:
            if usage.model not in self.by_model:
                self.by_model[usage.model] = {"calls": 0, "prompt": 0, "completion": 0, "total": 0}
            self.by_model[usage.model]["calls"] += 1
            self.by_model[usage.model]["prompt"] += usage.prompt_tokens
            self.by_model[usage.model]["completion"] += usage.completion_tokens
            self.by_model[usage.model]["total"] += usage.total_tokens

        # 保留历史（最多 1000 条）
        self.history.append(usage)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        logger.info(
            "Token usage: agent=%s model=%s prompt=%d completion=%d total=%d",
            usage.agent,
            usage.model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )

    def summary(self) -> dict[str, Any]:
        """返回统计摘要"""
        total_cost = sum(u.cost_estimate for u in self.history)
        return {
            "total_calls": self.total_calls,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "by_agent": self.by_agent,
            "by_model": self.by_model,
        }

    def reset(self) -> None:
        """重置统计"""
        self.total_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.by_agent.clear()
        self.by_model.clear()
        self.history.clear()


# 全局统计实例
_token_stats = TokenStats()


def get_token_stats() -> TokenStats:
    """获取全局 Token 统计实例"""
    return _token_stats


def reset_token_stats() -> None:
    """重置全局统计"""
    _token_stats.reset()
