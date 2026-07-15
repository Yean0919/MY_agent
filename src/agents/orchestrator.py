"""编排器 - 协调多个 Agent"""

import json
import re
from typing import Any

from src.core.agent import BaseAgent
from src.core.exceptions import AgentError
from src.core.llm import call_llm

# 简单任务关键词：匹配到这些模式的任务走快速通道（单 Agent）
_SIMPLE_TASK_PATTERNS = [
    r"写一个.*文件",
    r"保存.*文件",
    r"创建.*文件",
    r"生成.*代码",
    r"画一个",
    r"绘制",
    r"列出.*目录",
    r"list.*file",
    r"what files",
    r"hello|你好|hi|hey",
    r"解释|说明|什么是",
    r"计算",
]


def _is_simple_task(task: str) -> bool:
    """判断是否为简单任务（无需多 Agent 协作）"""
    task_lower = task.lower()
    for pattern in _SIMPLE_TASK_PATTERNS:
        if re.search(pattern, task_lower):
            return True
    # 很短的任务描述（< 20 字）大概率是简单任务
    return len(task) < 20


def _classify_simple_task(task: str) -> str:
    """对简单任务分类，决定用哪个 Agent"""
    if re.search(r"写|保存|创建|生成|画|绘制", task):
        return "coder"
    if re.search(r"测试|test|运行|run", task):
        return "tester"
    if re.search(r"搜索|查找|研究|search|research", task):
        return "researcher"
    if re.search(r"审查|review|检查", task):
        return "reviewer"
    # 默认用 coder
    return "coder"


class Orchestrator(BaseAgent):
    """编排器，负责协调多个 Agent 的工作"""

    def __init__(self) -> None:
        super().__init__(name="orchestrator", description="协调多个 Agent 的工作")
        self._agents: dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """注册 Agent

        Args:
            agent: Agent 实例
        """
        if not agent.name:
            raise ValueError("Agent name cannot be empty")
        self._agents[agent.name] = agent

    def unregister_agent(self, name: str) -> None:
        """注销 Agent

        Args:
            name: Agent 名称
        """
        self._agents.pop(name, None)

    def get_agent(self, name: str) -> BaseAgent | None:
        """获取 Agent

        Args:
            name: Agent 名称

        Returns:
            Agent 实例或 None
        """
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """列出所有已注册的 Agent

        Returns:
            Agent 名称列表
        """
        return list(self._agents.keys())

    async def _plan_agents(self, task: str) -> list[str]:
        """用 LLM 决定需要哪些 Agent 以及执行顺序

        Args:
            task: 任务描述

        Returns:
            Agent 名称列表（执行顺序）
        """
        available = list(self._agents.keys())
        if not available:
            return []

        try:
            plan_text = await call_llm(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"可用 Agent: {', '.join(available)}\n"
                            f"任务: {task}\n\n"
                            "请输出 JSON 数组，列出执行此任务需要的 Agent 名称及顺序。"
                            '例如: ["researcher", "coder", "reviewer", "tester"]'
                        ),
                    }
                ],
                system_prompt="你是一个任务编排专家。只输出 JSON 数组，不要其他内容。",
            )
            try:
                plan = json.loads(plan_text)
                if isinstance(plan, list):
                    # 过滤只保留已注册的 Agent
                    return [a for a in plan if a in self._agents]
            except json.JSONDecodeError:
                pass
        except RuntimeError:
            pass

        # 降级：默认全量执行
        return available

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行编排

        简单任务走快速通道（单 Agent），复杂任务走完整多 Agent 编排。

        Args:
            input_data: 输入数据，包含 task 字段

        Returns:
            编排结果

        Raises:
            AgentError: 编排错误
        """
        task = input_data.get("task", "")
        if not task:
            raise AgentError("Task cannot be empty")

        result = {"task": task, "plan": [], "results": []}

        # 快速通道：简单任务只调用一个 Agent，跳过 LLM 规划和多 Agent 串联
        if _is_simple_task(task):
            agent_name = _classify_simple_task(task)
            agent = self._agents.get(agent_name)
            if not agent:
                agent_name = "coder"
                agent = self._agents.get(agent_name)

            result["plan"] = [agent_name] if agent_name else []
            result["fast_path"] = True

            if agent:
                try:
                    context = {"task": task, "code_request": task}
                    agent_result = await agent.execute(context)
                    result["results"].append(
                        {
                            "agent": agent_name,
                            "status": "success",
                            "result": agent_result,
                        }
                    )
                except Exception as e:
                    result["results"].append(
                        {
                            "agent": agent_name,
                            "status": "error",
                            "message": str(e),
                        }
                    )
            else:
                result["results"].append(
                    {
                        "agent": agent_name,
                        "status": "error",
                        "message": f"No agent available for: {agent_name}",
                    }
                )
            return result

        # 完整编排：用 LLM 规划 Agent 执行顺序
        agent_names = await self._plan_agents(task)
        if not agent_names:
            agent_names = list(self._agents.keys())

        result["plan"] = agent_names
        result["fast_path"] = False

        # 串联执行：前一个 Agent 的输出作为后一个的输入
        context = {"task": task, "code_request": task}

        for agent_name in agent_names:
            agent = self._agents.get(agent_name)
            if not agent:
                result["results"].append(
                    {
                        "agent": agent_name,
                        "status": "error",
                        "message": f"Agent not found: {agent_name}",
                    }
                )
                continue

            try:
                agent_result = await agent.execute(context)
                result["results"].append(
                    {
                        "agent": agent_name,
                        "status": "success",
                        "result": agent_result,
                    }
                )

                # 把当前结果传递给下一个 Agent
                if agent_name == "coder":
                    context["code"] = agent_result.get("generated_code", "")
                    # 传递输出路径，让后续 Agent 知道文件位置
                    if agent_result.get("output_path"):
                        context["output_path"] = agent_result["output_path"]
                elif agent_name == "tester":
                    context["test_code"] = agent_result.get("test_code", "")

            except Exception as e:
                result["results"].append(
                    {
                        "agent": agent_name,
                        "status": "error",
                        "message": str(e),
                    }
                )

        return result
