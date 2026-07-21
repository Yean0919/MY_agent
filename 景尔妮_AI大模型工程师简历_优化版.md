# 景尔妮
## AI大模型工程师

📧 jingerni@example.com | 📱 138-xxxx-xxxx | 📍 北京 | 🔗 GitHub: github.com/jingerni

---

## 🎯 求职意向

**AI大模型工程师 / LLM应用工程师 / Agent开发工程师**

---

## 📝 个人总结

AI大模型全栈工程师，拥有从**基础理论到生产级系统**的完整技术栈。精通Transformer架构、LoRA微调、RAG系统、多Agent协作等核心技术。独立设计并实现了**Terminal Coding Agent（TCA）**——一个基于LangGraph的多Agent终端编程助手，具备AST+LSP双引擎代码理解、分层压缩记忆等生产级特性。具备**金融智能平台**、**电商客服多Agent系统**等多个大型项目经验。熟悉从模型训练、评估、量化到vLLM部署的全流程，具备Docker容器化、FastAPI服务化等工程化能力。

---

## 🛠️ 核心技术

**大模型/LLM：** Transformer、BERT、GPT、Qwen、DeepSeek、GLM、LiteLLM

**Agent框架：** LangGraph、CrewAI、AutoGen、ReAct、Plan-Execute

**RAG/检索：** LangChain、LlamaIndex、Milvus、Qdrant、FAISS、BGE、Reranker

**训练/微调：** SFT、LoRA、QLoRA、DPO、RLHF、LLaMA-Factory、Unsloth

**部署/推理：** vLLM、TGI、Ollama、Docker、SSE流式

**后端/API：** FastAPI、SQLAlchemy、Pydantic、JWT、Redis

**数据库：** MySQL、PostgreSQL、Milvus、Neo4j

**代码智能：** tree-sitter（AST）、pygls（LSP）、MCP SDK

---

## 💼 项目经历

### Terminal Coding Agent (TCA) —— 多Agent终端编程助手
**技术栈：** LangGraph · Textual · tree-sitter · LiteLLM · SQLite · MCP SDK

**项目描述：**
独立设计并实现基于LangGraph的多Agent终端AI编程助手，通过**LSP + AST双引擎**实现深度且低Token消耗的项目代码理解，通过**多Agent并行编排**提升复杂任务执行效率。

**核心成果：**
- **多Agent并行架构**：主Agent + Worker Agent池 + 知识提取Agent，并行加速比≥1.8x
- **LSP + AST双引擎**：tree-sitter解析源码 + MCP集成agent-lsp，节省30-84% Token
- **分层压缩记忆**：3层压缩策略 + SQLite FTS5全文检索，Token节省率≥40%
- **安全与容错**：BasePath校验、Bash黑名单、循环检测、熔断机制、自动恢复
- **质量门禁**：写文件后自动ruff/mypy检查，全链路Trace + TTFT监控

**项目价值：**
- 完整PRD/SDD/开发文档/模块手册/需求追溯矩阵
- 支持DeepSeek/Qwen/GLM等国产高性价比模型，通过LiteLLM支持100+提供商

---

### 金融智能平台 —— 多Agent+RAG+知识图谱金融AI系统
**技术栈：** LangGraph · FastAPI · SQLAlchemy · MySQL · Redis · Milvus · Neo4j · Vue 3

**项目描述：**
设计并实现大规模金融AI系统，结合多Agent工作流、混合RAG检索和知识图谱，为金融研究和风险控制提供智能化支持。

**核心成果：**
- **混合RAG流水线**：Milvus向量搜索 + BM25关键词搜索 + RRF融合排序 + BGE-Reranker重排序
- **知识图谱**：Neo4j图数据库，实体类型包括Company/Industry/RiskType/Regulator/Product
- **全栈架构**：FastAPI + SQLAlchemy(Async) + Alembic迁移 + Docker Compose部署

**项目价值：**
- 为金融研究和风险控制提供智能化支持
- 前端Vue 3 + ECharts仪表盘（风险KPI/趋势/分布饼图）

---

### 电商智能客服多Agent系统
**技术栈：** LangGraph · FastAPI · SQLAlchemy · Redis · Milvus · Neo4j · SSE

**项目描述：**
实现电商智能客服系统，采用Supervisor+6子Agent架构，支持订单/物流/售后/商品/FAQ/通用六大场景。

**核心成果：**
- **Supervisor路由**：JSON Mode结构化输出进行意图路由，LangGraph StateGraph条件边
- **多场景覆盖**：6个子Agent（order/logistics/postsale/product/faq/general）
- **技术栈**：MySQL + Milvus(FAQ RAG) + Neo4j(商品知识图谱) + Redis(限流)

**项目价值：**
- 提升客服效率，降低人工成本
- 支持SSE流式响应，用户体验良好

---

## 🎓 教育背景

**[学校名称]** | [学位] | [专业] | [毕业时间]

---

## 💼 工作经历

**[公司名称]** | [职位] | [工作时间]

---

## 📜 证书与荣誉

- [相关证书或荣誉]

---

## 🌟 其他技能

- **语言能力：** 英语（CET-6/托福/雅思）
- **软技能：** 团队协作、技术文档撰写、项目管理
- **开源贡献：** [GitHub开源项目链接]

---

## 📝 备注

- 简历中所有项目均为独立设计并实现
- 具备从0到1构建生产级AI系统的能力
- 熟悉AI大模型从训练到部署的全流程
- 对新技术保持敏感，持续学习前沿技术
