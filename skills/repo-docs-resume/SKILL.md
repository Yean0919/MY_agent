---
name: repo-docs-resume
description: Generate project documentation and resume project experience from a software repository. Use when the user asks Codex to read/analyze a GitHub or local code project and produce Markdown documents such as product development docs, system architecture docs, requirements docs, or resume project experience for a Python AI application developer or similar engineering role.
---

# Repo Docs Resume

## Overview

Use this skill to turn a repository into polished project documentation and resume-ready project experience. The workflow is optimized for AI application projects, especially Python/FastAPI/RAG/Agent/LLM systems, but applies to general software repositories.

For detailed section templates, read `references/output-templates.md` when drafting deliverables.

## Workflow

### 1. Establish Source Context

If the user provides a GitHub URL, clone or inspect the repository in the workspace. If the repository already exists locally, use the local copy.

Collect context in this order:

1. Repository tree with `rg --files`.
2. README and existing docs.
3. Dependency manifests such as `pyproject.toml`, `requirements.txt`, `package.json`, `docker-compose.yml`, Kubernetes manifests, CI files.
4. Application entry points and route/controller files.
5. Domain modules, service modules, models, repositories, tests, scripts, and frontend pages when present.

Prefer actual code over README claims when they conflict.

### 2. Identify The Product

Summarize:

- Product positioning and target users.
- Core business flows.
- Implemented modules.
- Partially implemented or mock-only modules.
- External services and deployment assumptions.
- Security, compliance, observability, and data consistency risks.

Do not inflate project maturity. Clearly distinguish:

- `已实现`
- `基础能力已存在`
- `前端 mock / 待接入真实数据`
- `规划或建议补齐`

### 3. Generate Three Project Documents

Unless the user asks for different names, create these Markdown deliverables:

- `产品开发文档.md`
- `系统架构文档.md`
- `需求文档.md`

Write them to the user-facing `outputs/` directory when available. If no special outputs directory exists, place them under `docs/generated/` or ask only if location matters.

Use Chinese by default when the user asks in Chinese.

### 4. Generate Resume Project Experience

When the user asks for resume content, generate:

- `简历项目经历.md`

Write from the requested role perspective. For "Python AI 应用开发工程师", emphasize:

- FastAPI/Python backend implementation.
- LLM service abstraction.
- RAG retrieval and document ingestion.
- Agent orchestration.
- Knowledge graph integration.
- Security and observability.
- Containerized deployment.

Keep claims defensible. Prefer engineering outcomes over unverifiable business metrics. Do not invent production user counts, revenue, accuracy improvements, latency numbers, or deployment scale unless they appear in source material or the user provides them.

### 5. Validate Deliverables

After writing files:

1. List output files and sizes.
2. Read the first lines of each generated file to catch path or encoding mistakes.
3. If the shell displays mojibake but the source text was written as UTF-8, mention only if it affects the actual file; do not rewrite needlessly.

## Documentation Rules

- Use Markdown tables for modules, APIs, requirements, and tech stacks.
- Use Mermaid diagrams for architecture and core flows when useful.
- Include concrete repository modules, paths, services, APIs, and configuration names.
- Include risks and improvement points.
- Avoid generic resume wording that could apply to any AI project.
- Avoid claiming responsibility for frontend UI if the requested role is backend/Python-focused; mention frontend collaboration only when relevant.
- For medical, legal, finance, or other high-stakes domains, include safety/compliance disclaimers and risk controls.

## Output Standards

Each deliverable should be self-contained:

- A reader should understand what the project does without opening the repository.
- The system architecture document should describe components, data stores, APIs, runtime flows, deployment, configuration, security, and observability.
- The requirements document should include roles, functional requirements, non-functional requirements, data consistency requirements, and acceptance criteria.
- The resume document should include both a detailed version and a concise resume-ready bullet version.

## Reference

Read `references/output-templates.md` before drafting if the user asks for one or more full documents.
