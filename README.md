# Terminal CodingAgent (TCA)

> 基于 Python 的多 Agent 协作编程平台 —— 通过 FastAPI 提供服务，Streamlit 提供可视化面板，支持对话式编程、任务编排、跨会话记忆和 MCP 工具接入。

[![CI](https://github.com/Yean0919/Project_demo/actions/workflows/ci.yml/badge.svg)](https://github.com/Yean0919/Project_demo/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 项目简介

Terminal CodingAgent (TCA) 是一个 **多 Agent 协作的编程助手平台**。用户通过对话或任务提交的方式下达指令，系统由 Orchestrator 编排多个专业 Agent（Coder、Reviewer、Tester、Researcher）协同完成代码生成、审查、测试和研究任务。

核心特点：

- **多 Agent 协作** — Orchestrator 根据任务复杂度自动规划 Agent 执行顺序，简单任务走快速通道（单 Agent），复杂任务走完整编排
- **对话式交互** — 基于 LLM 的多轮对话，支持工具调用（读/写/编辑文件、执行命令、搜索）
- **跨会话记忆** — 短期记忆（SQLite Checkpointer）+ 长期记忆（ChromaDB 向量库）
- **代码索引** — AST（tree-sitter）+ LSP（pygls）双引擎代码感知
- **Token 压缩** — 三层分层压缩（L1 摘要 / L2 细节 / L3 归档）
- **MCP + Skill 接入** — 支持 MCP 协议接入外部工具，Skill 三层懒加载
- **可视化面板** — Streamlit Dashboard，实时查看对话、任务队列、执行历史和性能指标

## 快速开始

### 环境要求

- Python 3.11+
- 一个 LLM API Key（支持 Anthropic / OpenAI / Google / SenseNova 兼容接口）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Yean0919/Project_demo.git
cd Project_demo

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux / Mac

# 安装依赖
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key 和模型配置：

```ini
# LLM 配置
LLM_DEFAULT_PROVIDER=openai
LLM_DEFAULT_MODEL=sensenova-6.7-flash-lite
LLM_BASE_URL=https://token.sensenova.cn/v1
OPENAI_API_KEY=你的API_Key
```

支持的 provider：`anthropic`、`openai`、`google`、`faux`。通过 `LLM_BASE_URL` 可对接任意 OpenAI 兼容接口（如 SenseNova）。

### 启动

需要**两个终端**：

**终端 1 — API 服务（核心）**

```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**终端 2 — 可视化面板**

```bash
streamlit run src/agents/visualization.py
```

打开浏览器访问 `http://localhost:8501`。

### Makefile 快捷命令

```bash
make run        # 启动 API 服务
make dashboard  # 启动可视化面板
make test       # 运行测试（含覆盖率）
make lint       # 代码检查（ruff + mypy）
make init       # 完整初始化（venv + config + install）
```

## 架构概览

```
用户
  │
  ├── Streamlit Dashboard (端口 8501)
  │     └── HTTP → FastAPI (端口 8000)
  │
  └── FastAPI 路由
        ├── /api/chat/        → ToolUsingAgent（对话 + 工具调用）
        ├── /api/agent/run    → Orchestrator（多 Agent 编排）
        ├── /api/memory/      → 记忆系统
        ├── /api/indexing/    → 代码索引
        └── /api/tools/       → 工具管理
```

### 多 Agent 协作流程

```
用户任务
  │
  ├─ 简单任务（< 20 字 / 关键词匹配）
  │     └─ 快速通道 → 单个 Agent（Coder / Tester / Researcher / Reviewer）
  │
  └─ 复杂任务
        ├─ Orchestrator 用 LLM 规划 Agent 执行顺序
        ├─ 串联执行：Coder → Reviewer → Tester → Researcher
        └─ 前一个 Agent 的输出作为后一个的输入
```

### Agent 角色

| Agent | 职责 | 输出 |
|-------|------|------|
| **Orchestrator** | 任务编排，决定执行哪些 Agent 及顺序 | 执行计划 + 结果汇总 |
| **Coder** | 生成代码并自动保存到文件 | `generated_code` + `output_path` |
| **Reviewer** | 代码审查（正确性、性能、安全、可维护性） | `review_result`（评分 + 问题 + 建议） |
| **Tester** | 生成 pytest 单元测试 | `test_code` + `test_result` |
| **Researcher** | 技术研究和分析 | `research_result`（发现 + 置信度） |

### 对话模式（ToolUsingAgent）

对话模式使用 `ToolUsingAgent`，支持多轮对话和工具调用。可用工具：

| 工具 | 功能 |
|------|------|
| `read` | 读取文件内容 |
| `write` | 写入文件（自动创建目录，写入后验证） |
| `edit` | 替换文件中的文本 |
| `bash` | 执行 shell 命令 |
| `search` | 在文件中搜索文本 |

## 项目结构

```
terminal-coding-agent/
├── src/
│   ├── core/               # 核心引擎
│   │   ├── agent.py        # Agent 基类
│   │   ├── llm.py          # LLM 调用层（LangChain）
│   │   ├── loop.py         # Think-Act-Observe 主循环
│   │   ├── state.py        # 全局状态定义
│   │   ├── session_manager.py  # 会话管理
│   │   └── task_store.py   # 任务队列（SQLite）
│   │
│   ├── agents/             # Agent 协作
│   │   ├── orchestrator.py # 编排器（含快速通道）
│   │   ├── tool_using_agent.py  # 对话式工具调用 Agent
│   │   ├── graph.py        # LangGraph StateGraph
│   │   ├── debate.py       # Maker-Checker 辩论机制
│   │   ├── visualization.py# Streamlit 可视化面板
│   │   └── roles/          # 角色专家
│   │       ├── coder.py    # 代码专家
│   │       ├── reviewer.py # 审查专家
│   │       ├── tester.py   # 测试专家
│   │       └── researcher.py# 研究专家
│   │
│   ├── api/                # FastAPI 服务
│   │   ├── app.py          # 应用入口
│   │   └── routes/         # 路由（chat / agent / memory / indexing / tools）
│   │
│   ├── memory/             # 记忆系统
│   │   ├── short_term/     # 短期记忆（Checkpointer + SessionState）
│   │   ├── long_term/      # 长期记忆（ChromaDB + 知识库）
│   │   ├── retrieval/      # 记忆检索
│   │   └── consolidation.py# 后台 LLM 提炼
│   │
│   ├── indexing/           # 代码索引
│   │   ├── ast/            # AST 引擎（tree-sitter）
│   │   ├── lsp/            # LSP 客户端（pygls）
│   │   ├── hybrid.py       # 混合索引
│   │   └── context_injector.py  # 上下文注入
│   │
│   ├── compression/        # Token 压缩
│   │   ├── layers/         # L1 摘要 / L2 细节 / L3 归档
│   │   ├── loop.py         # 压缩循环
│   │   └── serializer.py   # 序列化
│   │
│   ├── tools/              # 工具系统
│   │   ├── registry.py     # 工具注册表
│   │   ├── builtin/        # 内置工具（read / write / edit / bash / search）
│   │   ├── mcp/            # MCP 协议接入
│   │   └── skills/         # Skill 加载与执行
│   │
│   ├── config/             # 配置管理（pydantic-settings）
│   ├── middleware/         # 中间件钩子
│   ├── gui/                # Tkinter 配置 GUI
│   ├── server/             # 本地代理服务器
│   └── utils/              # 通用工具（日志 / 重试）
│
├── tests/                  # 测试（18 个测试文件）
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
├── skills/                 # Skill 定义
├── config/                 # 配置文件
├── scripts/                # 脚本工具
├── docs/                   # 详细文档
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── pyproject.toml          # 项目配置（ruff / mypy / pytest）
├── Makefile                # 快捷命令
└── .env.example            # 环境变量模板
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/chat/` | 发送对话消息 |
| GET | `/api/chat/sessions` | 列出所有会话 |
| GET | `/api/chat/history/{session_id}` | 获取会话历史 |
| DELETE | `/api/chat/session/{session_id}` | 删除会话 |
| POST | `/api/agent/run` | 提交任务（多 Agent 编排） |
| GET | `/api/agent/status/{task_id}` | 获取任务状态 |
| GET | `/api/agent/list` | 列出任务 |
| GET | `/api/agent/stats` | 任务统计 |

## 技术栈

| 层面 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| Web 框架 | FastAPI + Uvicorn |
| 可视化 | Streamlit |
| LLM 抽象 | LangChain + LangGraph |
| 长期记忆 | ChromaDB |
| 持久化 | SQLite |
| 代码索引 | tree-sitter + pygls |
| MCP 接入 | MCP Python SDK |
| 配置 | pydantic-settings |
| 代码质量 | ruff + mypy |
| 测试 | pytest + pytest-cov |

## 开发

### 运行测试

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### 代码检查

```bash
ruff check src/ tests/
ruff format src/ tests/ --check
mypy src/
```

### CI

推送或 PR 到 `main` / `develop` 分支时，GitHub Actions 自动运行：

1. ruff 检查 + 格式化检查
2. mypy 类型检查
3. pytest 测试（Python 3.11 + 3.12 双版本）
4. 覆盖率上传（Codecov）

## 文档

- [产品需求文档](docs/01_产品需求文档.md)
- [系统架构文档](docs/02_系统架构文档.md)
- [项目开发文档](docs/03_项目开发文档.md)
- [核心模块设计](docs/04_核心模块设计.md)
- [测试与运维手册](docs/05_测试与运维手册.md)
- [团队协作框架](PROJECT_FRAMEWORK.md)

## 许可证

MIT License
