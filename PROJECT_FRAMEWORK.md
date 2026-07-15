# Terminal CodingAgent — 五人团队协作框架

> 本文档定义项目结构、Git 工作流、模块分工与协作规范，确保五人并行开发时结构严谨、环环相扣。

---

## 一、项目目录结构

```
terminal-coding-agent/
├── .github/                          # GitHub 配置
│   ├── workflows/                    # CI/CD 流水线
│   │   ├── ci.yml                    # 持续集成
│   │   └── release.yml               # 发布流程
│   ├── ISSUE_TEMPLATE/               # Issue 模板
│   └── PULL_REQUEST_TEMPLATE.md      # PR 模板
│
├── docs/                             # 📚 文档中心（已存在）
│   ├── README.md                     # 项目总览
│   ├── 01_产品需求文档.md
│   ├── 02_系统架构文档.md
│   ├── 03_项目开发文档.md
│   ├── 04_核心模块设计.md
│   └── 05_测试与运维手册.md
│
├── src/                              # 🧠 源代码主目录
│   ├── __init__.py
│   │
│   ├── core/                         # 🔧 核心引擎层（公共基础）
│   │   ├── __init__.py
│   │   ├── agent.py                  # Agent 基类
│   │   ├── loop.py                   # Think-Act-Observe 主循环
│   │   ├── state.py                  # 全局状态定义
│   │   └── exceptions.py             # 自定义异常
│   │
│   ├── config/                       # ⚙️ 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py               # pydantic-settings 配置类
│   │   └── schemas.py                # 配置数据结构
│   │
│   ├── middleware/                   # 🔗 中间件钩子（横切能力）
│   │   ├── __init__.py
│   │   ├── base.py                   # 钩子基类
│   │   ├── hooks.py                  # 内置钩子实现
│   │   └── registry.py              # 钩子注册表
│   │
│   ├── agents/                      # 🤖 多 Agent 协作模块 [成员A]
│   │   ├── __init__.py
│   │   ├── graph.py                  # LangGraph StateGraph 定义
│   │   ├── orchestrator.py           # 编排器
│   │   ├── roles/                    # 角色专家池
│   │   │   ├── __init__.py
│   │   │   ├── coder.py              # 代码专家
│   │   │   ├── reviewer.py           # 审查专家
│   │   │   ├── tester.py             # 测试专家
│   │   │   └── researcher.py         # 研究专家
│   │   ├── debate.py                 # Maker-Checker 辩论机制
│   │   └── visualization.py          # Streamlit 可视化面板
│   │
│   ├── memory/                      # 🧠 记忆系统模块 [成员B]
│   │   ├── __init__.py
│   │   ├── short_term/               # 短期记忆
│   │   │   ├── __init__.py
│   │   │   ├── checkpointer.py       # LangGraph Checkpointer
│   │   │   └── session_state.py      # 会话状态管理
│   │   ├── long_term/                # 长期记忆
│   │   │   ├── __init__.py
│   │   │   ├── chroma_store.py       # ChromaDB 向量存储
│   │   │   └── knowledge_base.py     # 知识库管理
│   │   ├── retrieval/                # 记忆检索
│   │   │   ├── __init__.py
│   │   │   └── retriever.py          # 检索策略
│   │   └── consolidation.py          # 后台 LLM 提炼
│   │
│   ├── indexing/                    # 📖 代码索引模块 [成员C]
│   │   ├── __init__.py
│   │   ├── ast/                      # AST 引擎
│   │   │   ├── __init__.py
│   │   │   ├── parser.py             # tree-sitter 解析器
│   │   │   └── symbols.py            # 符号提取
│   │   ├── lsp/                      # LSP 引擎
│   │   │   ├── __init__.py
│   │   │   ├── client.py             # pygls 客户端
│   │   │   └── features.py           # LSP 功能封装
│   │   ├── hybrid.py                 # 双引擎融合
│   │   └── context_injector.py       # 上下文 Token 注入
│   │
│   ├── compression/                 # 📦 Token 压缩模块 [成员D]
│   │   ├── __init__.py
│   │   ├── layers/                   # 分层压缩
│   │   │   ├── __init__.py
│   │   │   ├── l1_summary.py         # L1 摘要层
│   │   │   ├── l2_detail.py          # L2 细节层
│   │   │   └── l3_archive.py         # L3 归档层
│   │   ├── serializer.py             # SessionState 序列化
│   │   └── loop.py                   # 五段闭环
│   │       # Intent→Context→Action→Observe→Adjustment
│   │
│   ├── tools/                       # 🔌 MCP + Skill 模块 [成员E]
│   │   ├── __init__.py
│   │   ├── mcp/                      # MCP 接入
│   │   │   ├── __init__.py
│   │   │   ├── client.py             # MCP SDK 客户端
│   │   │   ├── bridge.py             # 语言桥接
│   │   │   └── config.py             # MCP 服务器配置
│   │   ├── skills/                   # Skill 引擎
│   │   │   ├── __init__.py
│   │   │   ├── loader.py             # Markdown 懒加载器
│   │   │   ├── registry.py           # Skill 注册表
│   │   │   └── executor.py           # Skill 执行器
│   │   └── builtin/                  # 内置工具
│   │       ├── __init__.py
│   │       ├── bash.py
│   │       ├── read.py
│   │       └── write.py
│   │
│   ├── api/                         # 🌐 API 服务层
│   │   ├── __init__.py
│   │   ├── app.py                    # FastAPI 应用
│   │   ├── routes/                   # 路由
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── memory.py
│   │   │   └── health.py
│   │   └── schemas/                  # 请求/响应模型
│   │       ├── __init__.py
│   │       └── requests.py
│   │
│   └── utils/                       # 🛠️ 通用工具
│       ├── __init__.py
│       ├── logger.py                 # structlog 日志
│       ├── retry.py                  # tenacity 重试
│       └── types.py                  # 类型别名
│
├── tests/                           # 🧪 测试目录
│   ├── conftest.py                   # pytest fixtures
│   ├── unit/                         # 单元测试
│   │   ├── test_agents/
│   │   ├── test_memory/
│   │   ├── test_indexing/
│   │   ├── test_compression/
│   │   └── test_tools/
│   ├── integration/                  # 集成测试
│   │   ├── test_agent_flow.py
│   │   └── test_mcp_integration.py
│   └── e2e/                          # 端到端测试
│       └── test_full_workflow.py
│
├── skills/                          # 📁 Skill 定义目录
│   ├── README.md
│   └── example_skill/
│       ├── SKILL.md
│       └── scripts/
│
├── config/                          # 📝 配置文件
│   ├── mcp_servers.yaml              # MCP 服务器配置
│   └── logging.yaml                  # 日志配置
│
├── data/                            # 💾 数据目录（gitignore）
│   ├── chroma/
│   ├── checkpoints/
│   └── app.db
│
├── scripts/                         # 📜 脚本工具
│   ├── setup.sh                      # 环境初始化
│   ├── lint.sh                       # 代码检查
│   └── test.sh                       # 测试运行
│
├── .env.example                     # 环境变量模板
├── .gitignore
├── .pre-commit-config.yaml          # pre-commit 配置
├── pyproject.toml                   # 项目配置
├── requirements.txt                 # 生产依赖
├── requirements-dev.txt             # 开发依赖
├── Makefile                         # 常用命令
└── README.md                        # 项目说明
```

---

## 二、Git 分支策略

### 2.1 分支模型（Git Flow 简化版）

```
main (主分支)
  │
  ├── develop (开发主线)
  │     │
  │     ├── feature/multi-agent      [成员A]
  │     ├── feature/memory-system    [成员B]
  │     ├── feature/code-indexing    [成员C]
  │     ├── feature/token-compression[成员D]
  │     └── feature/mcp-skill        [成员E]
  │
  ├── release/v1.0 (发布分支)
  │
  └── hotfix/xxx (紧急修复)
```

### 2.2 分支命名规范

| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| 功能分支 | `feature/<模块名>-<功能>` | `feature/agents-orchestrator` |
| 修复分支 | `fix/<问题描述>` | `fix/memory-leak` |
| 发布分支 | `release/v<版本>` | `release/v1.0.0` |
| 热修复 | `hotfix/<问题描述>` | `hotfix/crash-on-startup` |

### 2.3 提交规范（Conventional Commits）

```
<type>(<scope>): <subject>

[可选 body]

[可选 footer]
```

**类型说明**：

| type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(agents): add orchestrator` |
| `fix` | 修复 | `fix(memory): resolve connection leak` |
| `docs` | 文档 | `docs(api): update README` |
| `style` | 格式 | `style: run ruff formatter` |
| `refactor` | 重构 | `refactor(core): extract base class` |
| `test` | 测试 | `test(memory): add unit tests` |
| `chore` | 构建 | `chore: update dependencies` |

---

## 三、五人分工详解

### 3.1 成员分工总览

| 成员 | 负责模块 | 核心职责 | 分支 |
|------|---------|---------|------|
| **成员A** | `src/agents/` | 多 Agent 协作与可视化 | `feature/multi-agent` |
| **成员B** | `src/memory/` | 跨会话记忆系统 | `feature/memory-system` |
| **成员C** | `src/indexing/` | LSP + AST 代码索引 | `feature/code-indexing` |
| **成员D** | `src/compression/` | Token 压缩与会话持久化 | `feature/token-compression` |
| **成员E** | `src/tools/` | MCP + Skill 接入 | `feature/mcp-skill` |

### 3.2 各成员详细任务

#### 🤖 成员A：多 Agent 协作与可视化

**核心文件**：
- `src/agents/graph.py` — LangGraph StateGraph 定义
- `src/agents/orchestrator.py` — 编排器实现
- `src/agents/roles/*.py` — 4个角色专家
- `src/agents/debate.py` — Maker-Checker 辩论
- `src/agents/visualization.py` — Streamlit 面板

**任务清单**：

| 序号 | 任务 | 依赖 | 交付物 |
|------|------|------|--------|
| A1 | 定义 AgentState 数据结构 | core/state.py | graph.py |
| A2 | 实现 LangGraph StateGraph | A1 | graph.py |
| A3 | 实现 Orchestrator 编排器 | A2 | orchestrator.py |
| A4 | 实现 Coder 角色 | A2 | roles/coder.py |
| A5 | 实现 Reviewer 角色 | A2 | roles/reviewer.py |
| A6 | 实现 Tester 角色 | A2 | roles/tester.py |
| A7 | 实现 Researcher 角色 | A2 | roles/researcher.py |
| A8 | 实现 Maker-Checker 辩论 | A3, A5 | debate.py |
| A9 | 实现 Streamlit 可视化 | A3 | visualization.py |
| A10 | 集成测试 | A1-A9 | tests/ |

**接口定义**（供其他成员调用）：

```python
# src/agents/graph.py
from langgraph.graph import StateGraph
from src.core.state import AgentState

def create_agent_graph() -> StateGraph:
    """创建多 Agent 协作图"""
    ...

async def run_agent_task(task: str, config: dict) -> AgentState:
    """执行 Agent 任务"""
    ...
```

---

#### 🧠 成员B：跨会话记忆系统

**核心文件**：
- `src/memory/short_term/checkpointer.py` — LangGraph Checkpointer
- `src/memory/short_term/session_state.py` — 会话状态
- `src/memory/long_term/chroma_store.py` — ChromaDB 存储
- `src/memory/long_term/knowledge_base.py` — 知识库
- `src/memory/retrieval/retriever.py` — 检索策略
- `src/memory/consolidation.py` — 后台提炼

**任务清单**：

| 序号 | 任务 | 依赖 | 交付物 |
|------|------|------|--------|
| B1 | 实现 SQLite Checkpointer | core/state.py | checkpointer.py |
| B2 | 实现 SessionState 管理 | B1 | session_state.py |
| B3 | 实现 ChromaDB 存储层 | — | chroma_store.py |
| B4 | 实现知识库管理 | B3 | knowledge_base.py |
| B5 | 实现检索策略 | B3, B4 | retriever.py |
| B6 | 实现后台 LLM 提炼 | B3, B5 | consolidation.py |
| B7 | 实现记忆接口统一层 | B1-B6 | `__init__.py` |
| B8 | 集成测试 | B1-B7 | tests/ |

**接口定义**：

```python
# src/memory/__init__.py
class MemoryManager:
    """统一记忆管理接口"""
    
    async def save_checkpoint(self, state: AgentState) -> str:
        """保存检查点"""
        ...
    
    async def load_checkpoint(self, checkpoint_id: str) -> AgentState:
        """加载检查点"""
        ...
    
    async def store_knowledge(self, content: str, metadata: dict) -> str:
        """存储知识到长期记忆"""
        ...
    
    async def retrieve_context(self, query: str, top_k: int = 5) -> list:
        """检索相关上下文"""
        ...
```

---

#### 📖 成员C：LSP + AST 双引擎索引

**核心文件**：
- `src/indexing/ast/parser.py` — tree-sitter 解析器
- `src/indexing/ast/symbols.py` — 符号提取
- `src/indexing/lsp/client.py` — pygls 客户端
- `src/indexing/lsp/features.py` — LSP 功能封装
- `src/indexing/hybrid.py` — 双引擎融合
- `src/indexing/context_injector.py` — 上下文注入

**任务清单**：

| 序号 | 任务 | 依赖 | 交付物 |
|------|------|------|--------|
| C1 | 实现 tree-sitter 解析器 | — | parser.py |
| C2 | 实现符号提取（函数/类/变量） | C1 | symbols.py |
| C3 | 实现 pygls LSP 客户端 | — | client.py |
| C4 | 实现 LSP 功能封装 | C3 | features.py |
| C5 | 实现双引擎融合策略 | C2, C4 | hybrid.py |
| C6 | 实现上下文 Token 注入 | C5 | context_injector.py |
| C7 | 集成测试 | C1-C6 | tests/ |

**接口定义**：

```python
# src/indexing/__init__.py
class CodeIndexer:
    """双引擎代码索引器"""
    
    async def index_file(self, file_path: str) -> dict:
        """索引单个文件"""
        ...
    
    async def search_symbols(self, query: str, symbol_type: str = None) -> list:
        """搜索符号"""
        ...
    
    async def get_context(self, file_path: str, line: int, token_budget: int) -> str:
        """获取上下文注入"""
        ...
```

---

#### 📦 成员D：Token 压缩与会话持久化

**核心文件**：
- `src/compression/layers/l1_summary.py` — L1 摘要层
- `src/compression/layers/l2_detail.py` — L2 细节层
- `src/compression/layers/l3_archive.py` — L3 归档层
- `src/compression/serializer.py` — SessionState 序列化
- `src/compression/loop.py` — 五段闭环

**任务清单**：

| 序号 | 任务 | 依赖 | 交付物 |
|------|------|------|--------|
| D1 | 定义 SessionState 数据结构 | core/state.py | serializer.py |
| D2 | 实现 L1 摘要压缩 | D1 | l1_summary.py |
| D3 | 实现 L2 细节保留 | D1 | l2_detail.py |
| D4 | 实现 L3 归档策略 | D1 | l3_archive.py |
| D5 | 实现五段闭环逻辑 | D2-D4 | loop.py |
| D6 | 实现序列化/反序列化 | D1 | serializer.py |
| D7 | 集成测试 | D1-D6 | tests/ |

**接口定义**：

```python
# src/compression/__init__.py
class TokenCompressor:
    """分层 Token 压缩器"""
    
    async def compress(self, messages: list, target_tokens: int) -> list:
        """压缩消息到目标 Token 数"""
        ...
    
    async def decompress(self, compressed_state: SessionState) -> list:
        """解压缩消息"""
        ...
    
    async def run_loop(self, intent: str, context: dict) -> dict:
        """执行五段闭环"""
        # Intent → Context → Action → Observe → Adjustment
        ...
```

---

#### 🔌 成员E：MCP + Skill 接入

**核心文件**：
- `src/tools/mcp/client.py` — MCP SDK 客户端
- `src/tools/mcp/bridge.py` — 语言桥接
- `src/tools/mcp/config.py` — MCP 配置
- `src/tools/skills/loader.py` — Markdown 懒加载器
- `src/tools/skills/registry.py` — Skill 注册表
- `src/tools/skills/executor.py` — Skill 执行器
- `src/tools/builtin/*.py` — 内置工具

**任务清单**：

| 序号 | 任务 | 依赖 | 交付物 |
|------|------|------|--------|
| E1 | 实现 MCP 客户端封装 | — | client.py |
| E2 | 实现语言桥接（stdio/SSE） | E1 | bridge.py |
| E3 | 实现 MCP 配置管理 | E1 | config.py |
| E4 | 实现 SKILL.md 懒加载器 | — | loader.py |
| E5 | 实现 Skill 注册表 | E4 | registry.py |
| E6 | 实现 Skill 执行器 | E4, E5 | executor.py |
| E7 | 实现内置工具（bash/read/write） | — | builtin/*.py |
| E8 | 集成测试 | E1-E7 | tests/ |

**接口定义**：

```python
# src/tools/__init__.py
class ToolManager:
    """统一工具管理器"""
    
    async def register_mcp_server(self, config: dict) -> None:
        """注册 MCP 服务器"""
        ...
    
    async def load_skill(self, skill_path: str) -> Skill:
        """懒加载 Skill"""
        ...
    
    async def execute_tool(self, tool_name: str, params: dict) -> any:
        """执行工具"""
        ...
    
    def list_available_tools(self) -> list:
        """列出可用工具"""
        ...
```

---

## 四、模块依赖关系图

```
                    ┌─────────────────────────────────────────┐
                    │              core/                       │
                    │  (agent.py, loop.py, state.py)          │
                    └──────────────┬──────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   agents/       │    │   memory/       │    │   indexing/     │
│  [成员A]        │◄──►│  [成员B]        │◄──►│  [成员C]        │
│                 │    │                 │    │                 │
│ - graph         │    │ - checkpointer  │    │ - ast/parser    │
│ - orchestrator  │    │ - chroma_store  │    │ - lsp/client    │
│ - roles/*       │    │ - retriever     │    │ - hybrid        │
│ - debate        │    │ - consolidation │    │ - context_inject│
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         │         ┌────────────┼────────────┐         │
         │         │            │            │         │
         ▼         ▼            ▼            ▼         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      middleware/                                │
│                    (钩子机制 - 横切能力)                         │
└─────────────────────────────────────────────────────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  compression/   │    │   tools/        │    │     api/        │
│  [成员D]        │    │  [成员E]        │    │   (公共)        │
│                 │    │                 │    │                 │
│ - l1_summary    │    │ - mcp/client    │    │ - FastAPI       │
│ - l2_detail     │    │ - skills/loader │    │ - routes        │
│ - l3_archive    │    │ - builtin/*     │    │ - schemas       │
│ - loop          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 依赖矩阵

| 模块 | 依赖模块 | 被依赖模块 |
|------|---------|-----------|
| core | 无 | agents, memory, indexing, compression, tools |
| agents | core, memory, indexing, tools | api |
| memory | core | agents, compression |
| indexing | core | agents |
| compression | core, memory | agents |
| tools | core | agents |
| middleware | core | agents, memory, indexing, compression, tools |
| api | agents | 无 |

---

## 五、开发阶段与里程碑

### 5.1 两阶段开发策略

```
阶段一：并行开发（D1-D8）
├── 成员A：agents 基础框架
├──成员B：memory 短期记忆
├── 成员C：ast 索引引擎
├── 成员D：compression 基础层
└── 成员E：mcp 基础接入

阶段二：集成联调（D9-D14）
├── 成员A：可视化 + 辩论机制
├── 成员B：长期记忆 + 提炼
├── 成员C：LSP + 双引擎融合
├── 成员D：五段闭环 + 持久化
└── 成员E：Skill 引擎 + 内置工具
```

### 5.2 详细里程碑

| 里程碑 | 时间 | 目标 | 验收条件 |
|--------|------|------|---------|
| **M1 基础骨架** | D1-D4 | 跑通核心框架 | core 模块可运行 |
| **M2 模块独立** | D5-D8 | 各模块独立可测 | 5个模块单元测试通过 |
| **M3 集成联调** | D9-D12 | 模块间联调 | 端到端流程可跑通 |
| **M4 验收发布** | D13-D14 | 全流程验收 | 全部测试通过 + 文档完善 |

### 5.3 每周交付计划

| 周 | 成员A | 成员B | 成员C | 成员D | 成员E |
|----|-------|-------|-------|-------|-------|
| W1 | AgentState + Graph | Checkpointer | tree-sitter 解析 | SessionState 结构 | MCP 客户端 |
| W2 | Orchestrator + 2角色 | ChromaDB 存储 | 符号提取 | L1/L2 压缩 | Skill 加载器 |
| W3 | 剩余角色 + 辩论 | 检索策略 | LSP 客户端 | L3 归档 + 闭环 | 内置工具 |
| W4 | Streamlit 可视化 | 后台提炼 + 集成 | 双引擎融合 + 集成 | 序列化 + 集成 | 集成测试 |

---

## 六、协作规范

### 6.1 代码审查流程

```
开发完成
    ↓
创建 PR → 自动触发 CI
    ↓
指定 Reviewer（至少1人）
    ↓
Code Review
    ↓
修改 → 再次 Review
    ↓
批准 → 合并到 develop
```

**Review 规则**：
- 每个 PR 至少需要 1 个 Approval
- CI 必须通过（lint + test）
- 代码覆盖率不能下降

### 6.2 PR 模板

```markdown
## 描述
简要说明本次改动

## 改动类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 重构
- [ ] 文档更新

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 关联 Issue
Closes #xxx

## 截图（如有 UI 改动）
```

### 6.3 每日站会（可选）

- **时间**：每天 10:00，15分钟
- **内容**：
  1. 昨天完成了什么
  2. 今天计划做什么
  3. 遇到什么阻塞

### 6.4 冲突解决

| 冲突类型 | 解决方式 |
|---------|---------|
| 代码冲突 | 后合并者解决，与先合并者沟通 |
| 设计分歧 | 团队讨论，技术 Leader 决策 |
| 优先级冲突 | Product Owner 决策 |

---

## 七、环境与工具链

### 7.1 开发环境

| 工具 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行环境 |
| uv | latest | 包管理 |
| Git | 2.30+ | 版本控制 |
| VS Code / PyCharm | — | IDE |

### 7.2 代码质量工具

```yaml
# pyproject.toml 关键配置
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 7.3 Makefile 常用命令

```makefile
.PHONY: install lint test run

install:
	uv venv --python 3.12
	uv pip install -r requirements.txt
	uv pip install -r requirements-dev.txt

lint:
	ruff check src/ tests/
	ruff format src/ tests/
	mypy src/

test:
	pytest tests/ -v --cov=src

run:
	uvicorn src.api.app:app --reload

dashboard:
	streamlit run src/agents/visualization.py
```

---

## 八、快速开始（5分钟）

### 8.1 克隆与初始化

```bash
# 克隆仓库
git clone https://github.com/your-org/terminal-coding-agent.git
cd terminal-coding-agent

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 运行测试
make test

# 启动服务
make run
```

### 8.2 各成员启动开发

```bash
# 成员A：切换到 agents 分支
git checkout -b feature/multi-agent develop
cd src/agents
# 开始开发...

# 成员B：切换到 memory 分支
git checkout -b feature/memory-system develop
cd src/memory
# 开始开发...

# ...其他成员类似
```

---

## 九、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 接口不一致 | 集成困难 | 提前定义接口 + 代码审查 |
| 分支冲突 | 开发阻塞 | 频繁 rebase + 小步提交 |
| 依赖版本冲突 | 运行失败 | 锁定版本 + requirements.txt |
| 进度不同步 | 延期 | 每周同步 + 里程碑检查 |

---

## 十、参考文档

| 文档 | 用途 |
|------|------|
| `01_产品需求文档.md` | 了解项目目标与功能边界 |
| `02_系统架构文档.md` | 了解技术架构与设计决策 |
| `03_项目开发文档.md` | 了解编码规范与开发流程 |
| `04_核心模块设计.md` | 了解各模块详细设计 |
| `05_测试与运维手册.md` | 了解测试与部署流程 |

---

> **最后更新**：2026-07-14  
> **维护者**：TCA 团队
