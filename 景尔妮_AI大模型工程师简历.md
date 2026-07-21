# 景尔妮
## AI大模型全栈工程师

📧 jingerni@example.com | 📱 138-xxxx-xxxx | 📍 北京 | 🔗 GitHub: github.com/jingerni

---

## 🎯 求职意向

**AI大模型工程师 / LLM应用工程师 / Agent开发工程师**

---

## 📝 个人总结

AI大模型全栈工程师，拥有从**基础理论到生产级系统**的完整技术栈。精通Transformer架构、LoRA微调、RAG系统、多Agent协作、MCP协议等核心技术。独立设计并实现了**Terminal Coding Agent（TCA）**——一个基于LangGraph的多Agent终端编程助手，具备AST+LSP双引擎代码理解、分层压缩记忆、质量门禁等生产级特性。具备**金融智能平台**、**电商客服多Agent系统**、**多模态RAG系统**等多个大型项目经验。熟悉从模型训练、评估、量化到vLLM部署的全流程，具备Docker容器化、FastAPI服务化、SQLAlchemy ORM等工程化能力。

---

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| **大模型/LLM** | Transformer、BERT、GPT、Qwen、DeepSeek、GLM、LiteLLM、OpenRouter |
| **Agent框架** | LangGraph、CrewAI、DeepAgents、AutoGen、ReAct、Plan-Execute、Reflection |
| **RAG/检索** | LangChain、LlamaIndex、Milvus、Qdrant、FAISS、ChromaDB、BGE、Reranker、RRF |
| **训练/微调** | SFT、LoRA、QLoRA、DPO、RLHF、LLaMA-Factory、Unsloth、DeepSpeed ZeRO |
| **部署/推理** | vLLM、TGI、Ollama、Docker、Docker Compose、Nginx、SSE流式 |
| **量化/优化** | INT8/INT4、GGUF、FlashAttention、KV Cache、GQA、知识蒸馏 |
| **后端/API** | FastAPI、Uvicorn、SQLAlchemy 2.0、Alembic、PyMySQL、Pydantic v2、JWT |
| **数据库** | MySQL、PostgreSQL、SQLite、Redis、Milvus、Neo4j |
| **前端/UI** | Vue 3、Textual（TUI）、Streamlit、Tkinter、HTML/CSS/JavaScript |
| **代码智能** | tree-sitter（AST）、pygls（LSP）、MCP SDK、agent-lsp |
| **工具/协议** | MCP Server/Client、Skills系统、Function Calling、Tool Calling |
| **测试/质量** | pytest、ruff、mypy、pre-commit、GitHub Actions CI/CD、Codecov |
| **其他** | Python 3.11、PyTorch 2.10、NumPy、Pandas、Matplotlib、OpenCV、YOLO |

---

## 💼 项目经历

### 项目一：Terminal Coding Agent (TCA) —— 多Agent终端编程助手
**技术栈：** LangGraph · Textual · tree-sitter · LiteLLM · SQLite · Pydantic v2 · MCP SDK · Jinja2 · tiktoken

**项目描述：**
独立设计并实现了一个基于LangGraph的多Agent终端AI编程助手，旨在解决开发者在终端环境下的AI辅助编码痛点。系统通过**LSP + AST双引擎**实现深度且低Token消耗的项目代码理解，通过**多Agent并行编排**提升复杂任务执行效率，通过**结构化分层压缩与AST锚定的长期记忆**解决上下文窗口溢出与跨会话知识沉淀问题。

**核心架构（5层分层设计）：**
```
接入与交互层：Textual TUI四面板界面（任务队列/日志/状态栏/输入）
Agent编排层：LangGraph StateGraph（路由→规划→并行分发→合成→压缩→知识提取）
工具与知识层：内置工具(File/Bash/Git) + MCP协议 + AST/LSP双引擎 + FTS5记忆检索
基础设施层：SQLite持久化(Checkpoint/索引/记忆) + LiteLLM模型网关(100+提供商)
可观测性层：LangGraph StreamEvents全链路Trace + Token计数 + TTFT监控 + 审计日志
```

**核心特性：**

1. **多Agent并行架构**
   - 主Agent（InputRouter → TaskPlanner → ParallelDispatcher → ResultSynthesizer）
   - Worker Agent池（LangGraph Send机制动态实例化，隔离写入+显式合并）
   - 知识提取Agent（后置KnowledgeExtractor，提取项目约定更新记忆库）
   - 单Agent降级路径（Planner失败时自动降级为单Agent处理）

2. **LSP + AST双引擎代码理解**
   - AST层：tree-sitter解析源码，提取类/函数定义结构树，存入SQLite file_index表
   - LSP层：MCP集成agent-lsp（GCF格式输出，节省30-84% Token）
   - 检索链：任务描述 → AST检索相关文件 → LSP获取类型推断 → LLM生成核心功能摘要 → 注入State
   - 索引速度：≥80文件/秒（1000文件<15s）

3. **分层压缩与长期记忆**
   - 3层压缩策略：L1摘要 / L2详情 / L3归档
   - 5阶段自愈合循环：Intent→Context→Action→Observe→Adjustment
   - 长期记忆：SQLite FTS5全文检索 + AST hash锚定 + 生命周期管理（active/stale/deprecated）
   - 记忆双载体：SQLite表（结构化检索）+ YAML文件（人类可读写）
   - Token节省率：≥40%

4. **安全与容错**
   - BasePath校验：os.path.commonpath防路径穿越
   - Bash黑名单：正则匹配+高危关键词TUI确认，不可运行时关闭
   - 循环检测：三元组(tool_name, file_path, args_hash)连续3次拒绝
   - 熔断机制：简单任务5次/复杂重构20次工具调用上限
   - MCP Server崩溃自动恢复：指数退避重启(1s→2s→4s→8s，最多3次)
   - SQLite损坏自动恢复：integrity_check + 备份恢复 + DDL重建
   - 磁盘空间监控：低于500MB阻塞写入 + 自动清理临时文件

5. **质量门禁与可观测性**
   - 质量门禁中间件：写文件后自动ruff/mypy检查（Python）或npm lint/vue-tsc（前端）
   - 全链路Trace：LangGraph StreamEvents捕获节点执行/LLM调用/工具调用
   - TTFT三色监控：绿色<1.5s / 黄色1.5-3s / 红色>3s触发告警
   - Token熔断：单次会话>100k Token强制阻塞

**性能指标：**
- 并行加速比：3子任务≥1.8x，5+子任务≥2.2x
- Worker超时上限：60秒
- 压缩后Token节省：40-60%
- TUI渲染帧率：60fps（Textual保证）

**项目成果：**
- 完整PRD/SDD/开发文档/模块手册/需求追溯矩阵/术语表/ADR架构决策记录
- Smoke测试覆盖：路由器/熔断/文件锁/循环检测/压缩触发/Worker隔离
- 支持DeepSeek/Qwen/GLM等国产高性价比模型，通过LiteLLM+OpenRouter支持100+提供商

---

### 项目二：金融智能平台 —— 多Agent+RAG+知识图谱金融AI系统
**技术栈：** LangGraph · FastAPI · SQLAlchemy(Async) · Alembic · MySQL · Redis · Milvus · Neo4j · Vue 3 · ECharts · Docker Compose · Makefile

**项目描述：**
设计并实现了一个大规模金融AI系统，结合多Agent工作流、混合RAG检索和知识图谱，为金融研究和风险控制提供智能化支持。

**核心架构：**
```
LangGraph多Agent工作流：
Router(意图分类: research/risk/chat) → Retrieval → Knowledge Graph → Research/Risk Node → Response
```

**核心特性：**

1. **混合RAG流水线**
   - Milvus向量搜索（COSINE，top 20）+ BM25关键词搜索（jieba，top 20）
   - RRF融合排序（k=60）→ BGE-Reranker-v2-m3重排序（top 5）→ 上下文注入
   - 文档处理：MinerU(magic-pdf)解析PDF + BGE-large-zh-v1.5嵌入

2. **知识图谱**
   - Neo4j图数据库
   - 实体类型：Company/Industry/RiskType/Regulator/Product
   - 关系类型：BELONGS_TO/FACES_RISK/REGULATED_BY/OFFERS/RELATED_TO

3. **全栈架构**
   - 后端：FastAPI + SQLAlchemy(Async) + Alembic迁移 + MySQL + Redis + Milvus + Neo4j
   - 前端：Vue 3 + ECharts仪表盘（风险KPI/趋势/分布饼图）
   - 基础设施：Docker Compose(MySQL/Redis/Milvus/Neo4j) + Makefile开发命令

---

### 项目三：电商智能客服多Agent系统（Loop Engineering）
**技术栈：** LangGraph · FastAPI · SQLAlchemy · Pydantic · JWT · Redis · Milvus · Neo4j · SSE

**项目描述：**
实现了一个电商智能客服系统，采用Supervisor+6子Agent架构，支持订单/物流/售后/商品/FAQ/通用六大场景。

**核心架构：**
```
Supervisor(意图分类+路由) → 6个子Agent(order/logistics/postsale/product/faq/general)
```

**核心特性：**
- Supervisor使用JSON Mode结构化输出进行意图路由
- LangGraph StateGraph条件边路由
- 技术栈：MySQL + Milvus(FAQ RAG) + Neo4j(商品知识图谱) + Redis(限流)
- RAG：Milvus向量 + BM25 + RRF融合 + FlagReranker
- SSE流式输出

---

### 项目四：多模态RAG系统
**技术栈：** LangChain · Milvus · MinerU · DashScope · CLIP · FastAPI · Vue 3 · MySQL · SSE

**项目描述：**
实现了一个支持文本、图片、表格的多模态RAG系统，从PDF中解析复杂内容并进行跨模态检索。

**核心特性：**
- PDF解析：MinerU在线API（主）+ pdfplumber（备用）；复杂表格(>6列,>10行)额外裁剪为图片
- 父子分块策略：父块(1200字符,语义段落切分)保留完整上下文；子块(300字符,60重叠)精确检索
- 双多模态嵌入流水线（可切换）：
  - DashScope(qwen3-vl-embedding, 1024维)：文本+图片融合为单一向量，单集合+modality过滤
  - CLIP(clip-vit-base-patch32, 512维)：图片单独编码，查询融合文本0.6+图片0.4
- Milvus存储：两个集合(multimodal_rag文本 + multimodal_rag_mm多模态)，IVF_FLAT索引
- SSE流式聊天：支持纯文本和图片+文本混合查询，检索上下文侧边栏展示

---

### 项目五：AI Coding Harness —— AI编程脚手架
**技术栈：** LangGraph · FastAPI · SQLAlchemy · Pydantic · Docker · ruff · mypy · pytest

**项目描述：**
实现了一个AI编程脚手架系统，让AI能自主编写全栈代码并通过质量门禁。

**核心特性：**
- FullStackOrchestrator：文件系统工具/终端工具/Git工具/Web搜索工具
- 质量门禁中间件：@wrap_tool_call钩子，写文件后自动ruff check/mypy或npm run lint/vue-tsc
- 循环防止：ToolCallLimitMiddleware(run_limit=60)
- Git审批：HumanInTheLoopMiddleware(interrupt_on={"git_tool": True})
- 结构化输出：Pydantic FinalOutput(summary, commit_hash)
- 反幻觉Prompt：禁止运行服务/安装，要求写不熟悉API前先Web搜索

---

### 项目六：FastAPI + SQLAlchemy ORM全栈项目
**技术栈：** FastAPI · SQLAlchemy 2.0 · Alembic · PyMySQL · Pydantic v2 · Uvicorn

**项目描述：**
实现了多个FastAPI + SQLAlchemy项目，包括产品CRUD系统和学生选课四表系统。

**核心特性：**
- 连接池配置：pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600
- 依赖注入：get_db() + Session生命周期管理
- 多对多关系：学生↔课程通过Enrollment中间表（含成绩）
- Alembic迁移：版本控制数据库结构变更
- Pydantic Schema：ProductCreate/ProductUpdate/ProductResponse
- 完整CRUD：创建/读取(分页)/按ID读取/按价格范围搜索/部分更新/删除

---

## 🎓 教育背景

**XX大学 | 计算机科学与技术 | 本科 | 2022-2026**

---

## 📜 证书与荣誉

- 大模型全栈学习63天（2026.4.15-6.16），完成从零基础到生产级系统的完整学习
- AI大模型课程19天15节课（2026.6.8-6.26），覆盖注意力机制到RAG优化全链路
- Agent工程课程12天（2026.7.1-7.17），覆盖多模态RAG到Harness/Loop Engineering

---

## 📖 技术博客与开源

- GitHub: github.com/jingerni（Terminal Coding Agent开源项目）
- 技术博客：大模型全栈知识总结（17篇技术文章）

---

## 💡 自我评价

- **技术深度**：从Transformer底层原理到生产级Agent系统，具备完整技术栈
- **工程能力**：具备PRD/SDD/ADR文档编写能力，熟悉CI/CD、Docker、监控
- **学习能力**：63天从零基础到能独立设计生产级系统
- **问题解决**：擅长分析根因、设计容错方案、优化性能
- **沟通表达**：能用大白话解释复杂技术概念，具备技术文档编写能力

---

> 📅 简历生成日期：2026年7月17日
> 🎯 目标岗位：AI大模型工程师 / LLM应用工程师 / Agent开发工程师
