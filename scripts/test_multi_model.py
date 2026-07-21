"""快速测试多模型协作 — 验证不同 Agent 使用不同模型"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(name)s | %(message)s")

from src.agents.orchestrator import Orchestrator
from src.agents.roles.coder import CoderAgent
from src.agents.roles.reviewer import ReviewerAgent
from src.agents.roles.tester import TesterAgent


async def main():
    orchestrator = Orchestrator()

    # 注册 Agent（自动从 .env 读取模型映射）
    orchestrator.register_agent(CoderAgent())
    orchestrator.register_agent(ReviewerAgent())
    orchestrator.register_agent(TesterAgent())

    # 显示模型配置
    print("=" * 50)
    print("Agent 模型配置:")
    for name, profile in orchestrator.get_agent_model_info().items():
        print(f"  {name:12s} -> {profile or '(默认)'}")
    print("=" * 50)

    # 执行任务
    task = "写一个 Python 二分查找函数，要求有详细注释"
    print(f"\n任务: {task}\n")

    result = await orchestrator.execute({"task": task})

    print(f"\n执行计划: {result['plan']}")
    print(f"快速通道: {result.get('fast_path', False)}")

    for r in result["results"]:
        agent = r["agent"]
        status = r["status"]
        print(f"\n[{agent}] {status}")
        if status == "success":
            res = r["result"]
            if "generated_code" in res:
                print(f"  生成代码: {res['generated_code'][:100]}...")
            if "review_result" in res:
                print(f"  审查结果: {res['review_result']}")


if __name__ == "__main__":
    asyncio.run(main())
