"""LangGraph StateGraph 定义"""

from typing import Any

from src.core.state import AgentState


class AgentGraph:
    """多 Agent 协作图，使用 LangGraph StateGraph"""

    def __init__(self) -> None:
        self._nodes: dict[str, Any] = {}
        self._edges: list[tuple[str, str]] = []
        self._entry_point: str = ""

    def add_node(self, name: str, node_func: Any) -> None:
        """添加节点

        Args:
            name: 节点名称
            node_func: 节点函数
        """
        self._nodes[name] = node_func

    def add_edge(self, from_node: str, to_node: str) -> None:
        """添加边

        Args:
            from_node: 源节点
            to_node: 目标节点
        """
        if from_node not in self._nodes:
            raise ValueError(f"Node not found: {from_node}")
        if to_node not in self._nodes:
            raise ValueError(f"Node not found: {to_node}")
        self._edges.append((from_node, to_node))

    def set_entry_point(self, node_name: str) -> None:
        """设置入口节点

        Args:
            node_name: 节点名称
        """
        if node_name not in self._nodes:
            raise ValueError(f"Node not found: {node_name}")
        self._entry_point = node_name

    async def run(self, initial_state: AgentState) -> AgentState:
        """运行图

        Args:
            initial_state: 初始状态

        Returns:
            最终状态
        """
        if not self._entry_point:
            raise ValueError("Entry point not set")

        state = initial_state
        current_node: str | None = self._entry_point or None

        while current_node:
            # 执行当前节点
            node_func = self._nodes.get(current_node)
            if node_func:
                state = await node_func(state)

            # 找到下一个节点
            next_node = None
            for from_node, to_node in self._edges:
                if from_node == current_node:
                    next_node = to_node
                    break

            current_node = next_node

        return state

    def get_graph_info(self) -> dict[str, Any]:
        """获取图信息

        Returns:
            图信息字典
        """
        return {
            "nodes": list(self._nodes.keys()),
            "edges": self._edges,
            "entry_point": self._entry_point,
        }


def create_agent_graph() -> AgentGraph:
    """创建多 Agent 协作图

    Returns:
        AgentGraph 实例
    """
    graph = AgentGraph()

    # 添加节点
    graph.add_node("orchestrator", lambda state: state)
    graph.add_node("coder", lambda state: state)
    graph.add_node("reviewer", lambda state: state)
    graph.add_node("tester", lambda state: state)
    graph.add_node("researcher", lambda state: state)

    # 添加边
    graph.add_edge("orchestrator", "coder")
    graph.add_edge("coder", "reviewer")
    graph.add_edge("reviewer", "tester")
    graph.add_edge("tester", "researcher")

    # 设置入口
    graph.set_entry_point("orchestrator")

    return graph
