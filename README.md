# Terminal CodingAgent (TCA)

> 基于 Python 的多 Agent 协作编程平台 —— 通过 FastAPI 提供服务，Streamlit 提供可视化面板，支持多模型接入、对话式编程、任务编排、跨会话记忆和 MCP 工具接入。

[![CI](https://github.com/Yean0919/MY_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Yean0919/MY_agent/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 项目简介

Terminal CodingAgent (TCA) 是一个 **多 Agent 协作的编程助手平台**。用户通过对话或任务提交的方式下达指令，系统由 Orchestrator 编排多个专业 Agent（Coder、Reviewer、Tester、Researcher）协同完成代码生成、审查、测试和研究任务。

核心特点：

- **多 Agent 协作** — Orchestrator 根据任务复杂度自动规划 Agent 执行顺序，简单任务走快速通道（单 Agent），复杂任务走完整编排
- **多模型接入** — 不同 Agent 可配置不同模型（如 Coder 用 Agnes、Reviewer 用 SenseNova），Maker-Checker 异构审查避免同模型幻觉
- **对话式交互** — 基于 LLM 的多轮对话，支持工具调用（读/写/编辑文件、执行命令、搜索）
- **跨会话记忆** — 短期记忆（SQLite Checkpointer）+ 长期记忆（ChromaDB 向量库）
- **代码索引** — AST（tree-sitter）+ LSP（pygls）双引擎代码感知
- **Token 压缩** — 三层分层压缩（L1 摘要 / L2 细节 / L3 归档）
- **技能系统** — 5 项 AST 驱动的代码技能（审查/测试/重构/文档/Bug 排查）
- **MCP 接入** — 支持 MCP 协议接入外部工具，Skill 三层懒加载
- **可视化面板** — Streamlit Dashboard，实时查看对话、任务队列、执行历史和性能指标

## 快速开始

### 环境要求

- Python 3.11+
- 一个 LLM API Key（支持 Anthropic / OpenAI / Google / SenseNova / Agnes 等兼容接口）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Yean0919/MY_agent.git
cd MY_agent

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux / Mac

# 安装依赖
pip install -r requirements.txt

# 安装为可编辑模式（启用 yean 命令）
pip install -e .
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

支持的 provider：`anthropic`、`openai`、`google`、`faux`。通过 `LLM_BASE_URL` 可对接任意 OpenAI 兼容接口（如 SenseNova、Agnes AI）。

#### 多模型配置

不同 Agent 可以使用不同的模型，适用于 Maker-Checker 场景——避免同一模型既当裁判又当选手导致的幻觉问题。

在 `.env` 中添加模型 profile 和 Agent 映射：

```ini
# 定义模型 profile
LLM_PROFILE_AGNES_PROVIDER=openai
LLM_PROFILE_AGNES_MODEL=agnes-2.0-flash
LLM_PROFILE_AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
LLM_PROFILE_AGNES_API_KEY=你的Agnes_Key

LLM_PROFILE_SENSENOVA_PROVIDER=openai
LLM_PROFILE_SENSENOVA_MODEL=sensenova-6.7-flash-lite
LLM_PROFILE_SENSENOVA_BASE_URL=https://token.sensenova.cn/v1
LLM_PROFILE_SENSENOVA_API_KEY=你的SenseNova_Key

# Agent 模型映射（生成侧用 Agnes，审查侧用 SenseNova）
LLM_AGENT_MODEL_CODER=agnes
LLM_AGENT_MODEL_RESEARCHER=agnes
LLM_AGENT_MODEL_REVIEWER=sensenova
LLM_AGENT_MODEL_TESTER=sensenova
LLM_AGENT_MODEL_ORCHESTRATOR=sensenova
```

也可在代码中显式指定：

```python
from src.agents.roles.coder import CoderAgent
from src.agents.roles.reviewer import ReviewerAgent
from src.agents.debate import DebateMechanism

# Maker 和 Checker 使用不同模型
maker = CoderAgent(model_profile="agnes")
checker = ReviewerAgent(model_profile="sensenova")
debate = DebateMechanism(maker=maker, checker=checker)
```

### 启动

> **三种启动方式**：终端交互（推荐日常使用）、API 服务 + 可视化面板（完整平台）。

#### 方式一：终端交互（`yean` 命令）

安装为可编辑模式后，直接在终端运行 `yean` 即可开始对话式编程。所有输入统一走 Harness（TAOR 循环），由 LLM 自主决定是直接回复还是调用工具。

```bash
# 安装为可编辑模式（只需执行一次）
pip install -e .

# 启动终端交互
yean

# 单次执行（不进入交互模式）
yean "写一个快速排序函数"

# 指定会话
yean --session my_project "重构 auth 模块"

# 指定工作目录
yean --cwd /path/to/project "解释这个代码库"

# 指定模型 / provider
yean --provider openai --model sensenova-6.7-flash-lite "你好"
```

终端内置命令：

| 命令 | 功能 |
|------|------|
| `quit` / `exit` / `q` | 退出 |
| `memory` | 查看会话记忆 |
| `clear` | 清空当前会话 |
| `tools` | 列出可用工具 |
| `agents` | 列出已注册 Agent |
| `status` | 查看会话状态 |
| `help` | 显示帮助 |

#### 方式二：API 服务 + 可视化面板

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

#### 方式三：多模型测试脚本

```bash
python scripts/test_multi_model.py
```

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
        ├─ 每个 Agent 可使用不同的 LLM 模型（多模型异构）
        └─ 前一个 Agent 的输出作为后一个的输入
```

### Agent 角色与模型配置

| Agent | 职责 | 默认模型 | 输出 |
|-------|------|----------|------|
| **Orchestrator** | 任务编排，决定执行哪些 Agent 及顺序 | SenseNova | 执行计划 + 结果汇总 |
| **Coder** | 生成代码并自动保存到文件 | Agnes | `generated_code` + `output_path` |
| **Reviewer** | 代码审查（正确性、性能、安全、可维护性） | SenseNova | `review_result`（评分 + 问题 + 建议） |
| **Tester** | 生成 pytest 单元测试 | SenseNova | `test_code` + `test_result` |
| **Researcher** | 技术研究和分析 | Agnes | `research_result`（发现 + 置信度） |

### 技能系统

内置 5 项 AST 驱动的代码技能，覆盖开发全流程：

| 技能 | 命令 | 功能 |
|------|------|------|
| **code-review** | `python skills/code-review/scripts/review.py --file src/main.py` | 多维度代码审查（正确性/性能/安全/可维护性/风格） |
| **test-gen** | `python skills/test-gen/scripts/generate.py --file src/utils.py` | 分析函数签名自动生成 pytest 测试用例 |
| **refactor** | `python skills/refactor/scripts/analyze.py --dir src/` | 检测 8 种代码异味（长函数/多参数/深层嵌套/魔法数字等） |
| **api-doc** | `python skills/api-doc/scripts/generate.py --dir src/api/routes/` | 扫描 FastAPI/Flask 路由自动生成 API 文档 |
| **bug-hunt** | `python skills/bug-hunt/scripts/hunt.py --file src/main.py` | 检测常见 Bug 模式（空值访问/资源泄漏/异常吞没等） |

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
MY_agent/
├── src/
│   ├── core/               # 核心引擎
│   │   ├── agent.py        # Agent 基类（支持 model_profile）
│   │   ├── llm.py          # LLM 调用层（多模型 profile 支持）
│   │   ├── loop.py         # Think-Act-Observe 主循环
│   │   ├── state.py        # 全局状态定义
│   │   ├── session_manager.py  # 会话管理
│   │   └── task_store.py   # 任务队列（SQLite）
│   │
│   ├── agents/             # Agent 协作
│   │   ├── orchestrator.py # 编排器（含快速通道 + 多模型支持）
│   │   ├── tool_using_agent.py  # 对话式工具调用 Agent
│   │   ├── graph.py        # LangGraph StateGraph
│   │   ├── debate.py       # Maker-Checker 辩论机制
│   │   ├── visualization.py# Streamlit 可视化面板
│   │   └── roles/          # 角色专家（各自支持独立模型配置）
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
│   ├── config/             # 配置管理（pydantic-settings，支持多模型 profile）
│   ├── middleware/         # 中间件钩子
│   ├── gui/                # Tkinter 配置 GUI
│   ├── server/             # 本地代理服务器
│   └── utils/              # 通用工具（日志 / 重试）
│
├── skills/                 # 技能系统
│   ├── code-review/        # 代码审查技能
│   ├── test-gen/           # 测试生成技能
│   ├── refactor/           # 重构分析技能
│   ├── api-doc/            # API 文档生成技能
│   └── bug-hunt/           # Bug 排查技能
│
├── tests/                  # 测试（45 个测试用例）
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
├── scripts/                # 脚本工具
├── config/                 # 配置文件
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
| 多模型 | ModelProfile + LLM_PROFILE_* 环境变量 |
| 长期记忆 | ChromaDB |
| 持久化 | SQLite |
| 代码索引 | tree-sitter + pygls |
| MCP 接入 | MCP Python SDK |
| 技能系统 | AST 分析 + 三层懒加载 |
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

推送或 PR 到 `main` 分支时，GitHub Actions 自动运行：

1. ruff 检查 + 格式化检查
2. mypy 类型检查
3. pytest 测试（Python 3.11 + 3.12 双版本）

## 文档

- [产品需求文档](docs/01_产品需求文档.md)
- [系统架构文档](docs/02_系统架构文档.md)
- [项目开发文档](docs/03_项目开发文档.md)
- [核心模块设计](docs/04_核心模块设计.md)
- [测试与运维手册](docs/05_测试与运维手册.md)
- [团队协作框架](PROJECT_FRAMEWORK.md)

## 许可证

MIT License
